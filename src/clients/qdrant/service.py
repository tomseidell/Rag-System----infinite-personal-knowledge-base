from qdrant_client.models import PointStruct, PointIdsList, ExtendedPointId
from qdrant_client.models import Distance, VectorParams
from qdrant_client import QdrantClient, AsyncQdrantClient
from src.modules.chunk.model import Chunk
import os 
from dataclasses import dataclass
from src.clients.qdrant.exceptions import QdrantException
import logging 
from qdrant_client import models
from fastembed import SparseEmbedding, SparseTextEmbedding # embedding modell built by qdrant


@dataclass
class QdrantInsertResult:
    chunk_count:int
    chunk_ids:list[ExtendedPointId]

logger = logging.getLogger(__name__)


class QdrantService:
    def __init__(self):
        self.client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
        self.sparse_model = SparseTextEmbedding(model_name="prithivida/Splade_PP_en_v1")
        self.ensure_collection()


    def _sparse_embedding(self, chunk_texts: list[str]):
        try:
            # create list of sparse embedding based on text chunks
            sparse_embeddings: list[SparseEmbedding] = list(self.sparse_model.embed(chunk_texts))
            return sparse_embeddings
        except Exception as e:
            logger.error(f"Failed to create sparse embeddings with qdrant fastembed: {e}")
            raise QdrantException(operation="sparse_embeddings", detail=str(e))

    
    def ensure_collection(self):
        try:
            self.client.get_collection("second_brain")
        except:
            self.client.create_collection(
                collection_name="second_brain",
                vectors_config={
                    "dense": VectorParams(size=768, distance=Distance.COSINE),
                },
                sparse_vectors_config={
                    "sparse": models.SparseVectorParams()
                }
            )

    def insert_many_chunks(self, chunk_objects: list[Chunk], embeddings: list[list[float]]) -> QdrantInsertResult:
        all_chunk_ids = []
        
        # process and upload chunks in batches
        batch_size = 16 
        logger.info(f"QdrantService: Starting processing of {len(chunk_objects)} chunks in batches of {batch_size}.")

        for i in range(0, len(chunk_objects), batch_size):
            batch_chunk_objects = chunk_objects[i:i + batch_size]
            batch_dense_embeddings = embeddings[i:i + batch_size]
            batch_texts = [chunk.text for chunk in batch_chunk_objects]
            
            logger.info(f"Processing Qdrant batch {i // batch_size + 1}...")

            # get sparse embeddings for chunks text
            batch_sparse_embeddings = self._sparse_embedding(batch_texts)

            points_to_upload = []

            # create valid insert points for qdrant, containing dense, sparse and payload
            for chunk_obj, dense_vector, sparse_emb in zip(batch_chunk_objects, batch_dense_embeddings, batch_sparse_embeddings):
                points_to_upload.append(PointStruct(
                    id=chunk_obj.id,
                    vector={
                        "dense": dense_vector,
                        "sparse": models.SparseVector(
                            indices=sparse_emb.indices.tolist(),
                            values=sparse_emb.values.tolist()
                        )
                    },
                    payload={
                        "user_id": chunk_obj.user_id,
                        "document_id": chunk_obj.document_id,
                        "content": chunk_obj.text
                    }
                ))
                all_chunk_ids.append(chunk_obj.id)

            try:
                # upload chunks to qdrant db
                self.client.upsert(
                    collection_name="second_brain",
                    wait=True,
                    points=points_to_upload
                )
                logger.info(f"Qdrant batch {i // batch_size + 1} uploaded successfully.")
            except Exception as e:
                logger.error(f"Failed to insert batch to Qdrant: {e}")
                raise QdrantException(operation="insert_batch", detail=str(e))

        return QdrantInsertResult(
            chunk_count=len(all_chunk_ids),
            chunk_ids=all_chunk_ids
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
        self.sparse_model = SparseTextEmbedding(model_name="prithivida/Splade_PP_en_v1")


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
    
    async def get_matching_chunks(self, query_text:str, dense_vector, user_id:int):
        try:
            sparse_embedding = list(self.sparse_model.embed([query_text]))
            sparse_vector = sparse_embedding[0]

            result = await self.client.query_points(
                collection_name="second_brain",
                prefetch=[
                    models.Prefetch(
                        query=dense_vector,
                        using="dense",
                        limit=20
                    ),
                    models.Prefetch(
                        query=models.SparseVector(
                           indices=sparse_vector.indices.tolist(),
                           values=sparse_vector.values.tolist()
                        ),
                        using= "sparse",
                        limit=20
                    )
                ],
                query= models.FusionQuery(fusion=models.Fusion.RRF),
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="user_id",
                            match=models.MatchValue(value=user_id)
                        )
                    ]
                ),
                with_payload=True,
                limit=5
            )
            return result.points
        except Exception as e:
            raise QdrantException(
                operation="async:get_matching_chunks",
                detail=str(e)
            )