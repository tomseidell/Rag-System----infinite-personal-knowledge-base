import ollama
import os
from src.clients.ollama.exceptions import OllamaException
import logging
from typing import AsyncGenerator
import time
import gc


logger = logging.getLogger(__name__)



logger = logging.getLogger(__name__)


class OllamaService():
    def __init__(self):
        self.client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434"))

    def embed_text(self, chunks: list[str], batch_size: int = 2, max_retries_per_batch: int = 2):
        all_embeddings = []
        skipped_indices = []
        
        logger.info(f"Total chunks: {len(chunks)}, batch_size: {batch_size}")
        
        reset_after_n_batches = 4 

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            current_keep_alive = -1

            if batch_num % reset_after_n_batches == 0:
                logger.warning(f"Batch {batch_num} is a reset batch. Forcing model reload after this.")
                current_keep_alive = 0

            retry_count = 0
            batch_success = False
            
            while retry_count < max_retries_per_batch and not batch_success:
                try:
                    logger.info(f"Processing Batch {batch_num} ({len(batch)} chunks)... [Attempt {retry_count + 1}]")
                    
                    # dynamically restart ollamas embedding modell based on current_keep_alive var
                    response = self.client.embed(
                        model="nomic-embed-text", 
                        input=batch,
                        keep_alive=current_keep_alive
                    )
                    
                    # add successfull embeddings to global array 
                    all_embeddings.extend(response["embeddings"])
                    logger.info(f"Batch {batch_num} done")
                    batch_success = True

                    del response
                    gc.collect()

                    # when restarting ollama, wait 2 seconds untio next request
                    if current_keep_alive == 0:
                        logger.warning("Pausing for 2 seconds to allow Ollama to reset...")
                        time.sleep(2)
                    
                except ollama.ResponseError as e:
                    retry_count += 1
                    logger.error(f"Ollama ResponseError on Batch {batch_num} (Attempt {retry_count})")
                    logger.error(f"Error details: {e}")
                    
                    # if current try is less than max retries, retry to embed
                    if retry_count < max_retries_per_batch:
                        logger.warning(f"Retrying batch {batch_num} after 3 second pause...")
                        time.sleep(3)
                    else:
                        #skip batch after 2 retries 
                        logger.error(f"SKIPPING Batch {batch_num} after {max_retries_per_batch} failed attempts")
                        
                        # add embedding of 0's to array
                        for idx in range(len(batch)):
                            chunk_global_idx = i + idx
                            skipped_indices.append(chunk_global_idx)
                            all_embeddings.append([0.0] * 768)
                        
                        logger.warning(f"Added placeholder embeddings for skipped chunks: {skipped_indices[-len(batch):]}")
            #clear Ram
            del batch
            gc.collect()

        if skipped_indices:
            logger.warning(f"--- COMPLETED WITH WARNINGS: {len(skipped_indices)} chunks were skipped ---")
            logger.warning(f"Skipped chunk indices: {skipped_indices}")
        else:
            logger.info(f"--- STABILITY MODE SUCCESS: All {len(chunks)} chunks processed. ---")
        
        del chunks
        gc.collect()
        
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