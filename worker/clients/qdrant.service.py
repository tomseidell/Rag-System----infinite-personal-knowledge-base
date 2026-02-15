class QdrantService:
    def __init__(self):
        self.client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
        self.sparse_model = SparseTextEmbedding(
            model_name="prithivida/Splade_PP_en_v1",
            #providers=["CUDAExecutionProvider"] disable in development because docker is running with cpu only 
            )
        self.ensure_collection()


    def create_sparse_embedding(self, chunks: list[str], batch_size: int = 10):
        # global array saving all embeddings 
        all_embeddings: list[SparseEmbedding] = []
        logger.info(f"Total chunks: {len(chunks)}, batch_size: {batch_size}")
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            try:
                logger.info(f"Processing Sparse Batch {batch_num} ({len(batch)} chunks)...")
                # create sparse embedding for chunk of 10
                response = list(self.sparse_model.embed(batch)) 
                all_embeddings.extend(response)
                logger.info(f"Sparse Batch {batch_num} done")
                
            except Exception as e:
                logger.error(f"Sparse embedding failed on batch {batch_num}: {e}")
                raise QdrantException(operation="sparse_embeddings", detail=str(e))
        
        return all_embeddings 
    
    # check wether collection in qdrant already exists or needs to be created
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


    def insert_chunks(self, chunk_objects: list[Chunk], dense_embeddings: list[list[float]], sparse_embeddings:list[SparseEmbedding]):
        # point structure which is required by Qdrant 
        points_to_upload = []

        all_chunk_ids = []

        # create valid insert points for qdrant, containing dense, sparse and payload
        for chunk_obj, dense_vector, sparse_emb in zip(chunk_objects, dense_embeddings, sparse_embeddings):

            # create 1 point, containing dense, sparse and payload 
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
        except Exception as e:
            logger.error(f"Failed to insert Vectorrs to Qdrant: {e}")
            raise QdrantException(operation="insert_chunks", detail=str(e))

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
        
