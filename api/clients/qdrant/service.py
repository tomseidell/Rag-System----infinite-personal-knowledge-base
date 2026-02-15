from qdrant_client.models import PointStruct, PointIdsList, ExtendedPointId
from qdrant_client.models import Distance, VectorParams
from qdrant_client import QdrantClient, AsyncQdrantClient
from app.modules.chunk.model import Chunk
import os 
from dataclasses import dataclass
from app.clients.qdrant.exceptions import QdrantException
import logging 
from qdrant_client import models
from fastembed import SparseEmbedding, SparseTextEmbedding # embedding modell built by qdrant
import gc
import time


@dataclass
class QdrantInsertResult:
    chunk_count:int
    chunk_ids:list[ExtendedPointId]

logger = logging.getLogger(__name__)


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
                        limit=25
                    ), 
                    models.Prefetch(
                        query=models.SparseVector(
                           indices=sparse_vector.indices.tolist(),
                           values=sparse_vector.values.tolist()
                        ),
                        using= "sparse",
                        limit=15
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
                limit=3
            )
            return result.points
        except Exception as e:
            raise QdrantException(
                operation="async:get_matching_chunks",
                detail=str(e)
            )
        

        