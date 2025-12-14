from src.document.model import Document
from src.chunk.model import Chunk
from src.user.model import User

from PyPDF2 import PdfReader
from io import BytesIO
from celery import Celery
import os 
from langchain_text_splitters import RecursiveCharacterTextSplitter
import ollama
from src.chunk.schemas import ChunkCreate
from src.database import SyncSessionLocal
from src.chunk.repository import SyncChunkRepository
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from src.storage.service import StorageService

from qdrant_client.models import Distance, VectorParams

import logging
import base64
from src.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def process_document(content:bytes, document_id:int, user_id:int, filename:str, content_type:str):
    content_bytes = base64.b64decode(content)

    
    db = SyncSessionLocal()
    storage_service = StorageService()
    client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
    chunk_repo = SyncChunkRepository(db)


    try:
        client.get_collection("second_brain")
    except:
        client.create_collection(
            collection_name="second_brain",
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )

    storage_path = None
    chunk_ids = []

    try:
        reader = PdfReader(BytesIO(content_bytes)) # create new file with BytesIO wrapper => keeps file properties like read
        pages = []
        for page in reader.pages:
            page_string = page.extract_text()
            pages.append(page_string)
        text = "\n".join(pages)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 500,
            chunk_overlap=20,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " "
            ]
        )
        chunks = text_splitter.split_text(text)

        ollama_client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434"))
        response = ollama_client.embed(model="nomic-embed-text", input=chunks)
        embeddings = response["embeddings"]

        points = []

        text_with_vector = zip(chunks, embeddings)

        for i, pair in enumerate(text_with_vector, start=1): #enumerate = text + index (i + pair)
            chunk_text, vector = pair

            chunk_data = ChunkCreate( # create chunk for db 
                document_id= document_id,
                text= chunk_text,
                chunk_index = i,
                user_id = user_id
            )

            chunk = chunk_repo.create_chunk(chunk_data)
            chunk_ids.append(chunk.id)

            points.append(PointStruct(id = chunk.id, vector=vector, payload={"user_id":user_id, "document_id":document_id, "content": chunk_text}))
            

        operation = client.upsert(
            collection_name= "second_brain",
            wait= True,
            points= points
        )


        storage_path = storage_service.upload_file(
            content=content,
            filename=filename,
            user_id=user_id,
            content_type=content_type
        )

        document = db.query(Document).filter(Document.id == document_id, Document.user_id == user_id).first()
        
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        document.status= "completed"
        document.storage_path = storage_path
        document.chunk_count = len(points)
        db.commit()

    except Exception as e:
        db.rollback()

        if chunk_ids:
            try:
                client.delete(
                    collection_name="second_brain",
                    points_selector=chunk_ids
                )
            except Exception as qdrant_error:
                logger.error(f"Failed to cleanup Qdrant: {qdrant_error}")

        if storage_path: # delete from gcp storage 
            try:
                storage_service.delete_file(storage_path)
            except:
                pass  

        try:
            document = db.query(Document).filter(
                Document.id == document_id
            ).first()
            if document:
                document.status = "failed"
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update document status: {db_error}")
        
        raise
    
    finally:
        db.close()



