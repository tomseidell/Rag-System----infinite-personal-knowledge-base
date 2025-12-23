import ollama
import os
from src.clients.ollama.exceptions import OllamaException
import logging
from ollama import ChatResponse
from typing import AsyncIterator, AsyncGenerator
import time


logger = logging.getLogger(__name__)


class OllamaService():
    def __init__(self):
        self.client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434"))

    def embed_text(self, chunks: list[str], batch_size: int = 2, max_retries_per_batch: int = 2):
        all_embeddings = []
        skipped_indices = []
        
        logger.info(f"--- BRUTE FORCE STABILITY MODE ---")
        logger.info(f"Total chunks: {len(chunks)}, batch_size: {batch_size}")
        
        reset_after_n_batches = 4 

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            current_keep_alive = -1

            if batch_num % reset_after_n_batches == 0:
                logger.warning(f"Batch {batch_num} is a reset batch. Forcing model reload after this.")
                current_keep_alive = 0

            # Retry-Logik für jeden Batch
            retry_count = 0
            batch_success = False
            
            while retry_count < max_retries_per_batch and not batch_success:
                try:
                    logger.info(f"Processing Batch {batch_num} ({len(batch)} chunks)... [Attempt {retry_count + 1}]")
                    
                    # Log chunk details for debugging
                    for idx, chunk in enumerate(batch):
                        chunk_global_idx = i + idx
                        logger.debug(f"  Chunk {chunk_global_idx}: {len(chunk)} chars, first 50: {chunk[:50]}")
                    
                    response = self.client.embed(
                        model="nomic-embed-text", 
                        input=batch,
                        keep_alive=current_keep_alive
                    )
                    
                    all_embeddings.extend(response["embeddings"])
                    logger.info(f"Batch {batch_num} done ✓")
                    batch_success = True

                    if current_keep_alive == 0:
                        logger.warning("Pausing for 2 seconds to allow Ollama to reset...")
                        time.sleep(2)
                    
                except ollama.ResponseError as e:
                    retry_count += 1
                    logger.error(f"!!! Ollama ResponseError on Batch {batch_num} (Attempt {retry_count}) !!!")
                    logger.error(f"Error details: {e}")
                    
                    if retry_count < max_retries_per_batch:
                        logger.warning(f"Retrying batch {batch_num} after 3 second pause...")
                        time.sleep(3)
                    else:
                        # Nach allen Retries: Batch überspringen
                        logger.error(f"SKIPPING Batch {batch_num} after {max_retries_per_batch} failed attempts")
                        
                        # Füge leere Embeddings für die übersprungenen Chunks hinzu
                        for idx in range(len(batch)):
                            chunk_global_idx = i + idx
                            skipped_indices.append(chunk_global_idx)
                            # Füge einen Null-Vektor hinzu (oder eine andere Placeholder-Strategie)
                            all_embeddings.append([0.0] * 768)  # nomic-embed-text hat 768 Dimensionen
                        
                        logger.warning(f"Added placeholder embeddings for skipped chunks: {skipped_indices[-len(batch):]}")

        if skipped_indices:
            logger.warning(f"--- COMPLETED WITH WARNINGS: {len(skipped_indices)} chunks were skipped ---")
            logger.warning(f"Skipped chunk indices: {skipped_indices}")
        else:
            logger.info(f"--- STABILITY MODE SUCCESS: All {len(chunks)} chunks processed. ---")
        
        return all_embeddings

class OllamaServiceAsync():
    def __init__(self):
        self.client = ollama.AsyncClient(host=os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434"))
    
    async def embed_text(self, text:str)->str:
        try:
            response = await self.client.embed(model="nomic-embed-text", input=text)
            return response["embeddings"][0]
        except ollama.RequestError as e:
            logger.error(f"Ollama connection Error: {e}")
            raise OllamaException(
                operation="async_embed_text",
                detail=str(e)
            ) 

    async def create_message(self, texts:list[str], user_input)->AsyncGenerator[str , None]:
        try:
            input_string = "\n\n".join(texts)
            response= await self.client.chat(model="llama3", stream=True, messages=[
                {
                    "role": "user",
                    "content": f"Create a response and primarily focus on information from this string: {input_string}. If the string is empty or simply no relevant information to the message are given, answer the question with all your basic knowledge and do not rely on the information string. The user message or input is: {user_input}"
                }
            ])
            async for chunk in response:
                if chunk.message.content:
                    yield chunk.message.content
            
            
        except ollama.RequestError as e:
            logger.error(f"Ollama connection Error: {e}")
            raise OllamaException(
                operation="async_create_message",
                detail=str(e)
            ) 