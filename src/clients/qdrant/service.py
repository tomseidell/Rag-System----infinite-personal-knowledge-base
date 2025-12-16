from qdrant_client.models import PointStruct, PointIdsList, ExtendedPointId
from qdrant_client.models import Distance, VectorParams
from qdrant_client import QdrantClient, AsyncQdrantClient
from src.modules.chunk.model import Chunk
import os 
from dataclasses import dataclass
from src.clients.qdrant.exceptions import QdrantException
import logging 

@dataclass
class QdrantInsertResult:
    chunk_count:int
    chunk_ids:list[ExtendedPointId]

logger = logging.getLogger(__name__)


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
        self.ensure_collection()
    
    def ensure_collection(self):
        try:
            self.client.get_collection("second_brain")
        except:
            self.client.create_collection(
                collection_name="second_brain",
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )

    def insert_many_chunks(self, chunk_objects:list[Chunk], embeddings:list[list[float]]) ->QdrantInsertResult:
        try:
            chunk_ids = []
            points = []
            for chunk_obj, vector in zip(chunk_objects, embeddings):
                points.append(PointStruct(
                    id = chunk_obj.id,
                    vector=vector,
                    payload={"user_id":chunk_obj.user_id,
                            "document_id":chunk_obj.document_id,
                            "content": chunk_obj.text
                            }
                    ))
                chunk_ids.append(chunk_obj.id)


            self.client.upsert(
                collection_name= "second_brain",
                wait= True,
                points= points
            )

            return QdrantInsertResult(
                chunk_count=len(points),
                chunk_ids=chunk_ids
            )
        except Exception as e:
            logger.error(f"Failed to insert chunks to Qdrant: {e}")
            raise QdrantException(
                operation="insert_many_chunks",
                detail=str(e)
            )
 
    def delete_many_chunks(self, chunkIds:list[ExtendedPointId]):
        try:
            self.client.delete(
                collection_name="second_brain",
                points_selector=PointIdsList(points=chunkIds),
            )
            
        except Exception as e:
            logger.error(f"Failed to delete chunks from Qdrant: {e}")
            raise QdrantException(
                operation="delete_many_chunks",
                detail=str(e)
            )
        


class AsyncQdrantService:
    def __init__(self):
        self.client = AsyncQdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))    

    
    @classmethod
    async def create(cls):
        instance = cls()
        await instance.ensure_collection()
        return instance

    async def ensure_collection(self):
            try:
                await self.client.get_collection("second_brain")
            except:
                await self.client.create_collection("second_brain")


    async def delete_many_chunks(self,chunk_ids:list[ExtendedPointId]):
        try:
            await self.client.delete(
                collection_name="second_brain",
                points_selector=PointIdsList(points=chunk_ids),
            )
        except Exception as e:
            logger.error(f"Failed to delete chunks from Qdrant: {e}")
            raise QdrantException(
                operation="async:delete_many_chunks",
                detail=str(e)
            )