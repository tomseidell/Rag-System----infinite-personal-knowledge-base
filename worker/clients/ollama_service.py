import gc
import logging
import os
import time

import ollama

from shared.core.exceptions import OllamaException

logger = logging.getLogger(__name__)


class OllamaService:
    def __init__(self):
        self.client = ollama.Client(
            host=os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
        )

    def embed_text(
        self,
        chunks: list[str],
        batch_size: int = 10,
        max_retries_per_batch: int = 2,
    ) -> list[list[float]]:
        all_embeddings = []
        skipped_indices = []
        logger.info(f"Total chunks: {len(chunks)}, batch_size: {batch_size}")

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            batch_num = i // batch_size + 1
            retry_count = 0
            batch_success = False

            while retry_count < max_retries_per_batch and not batch_success:
                try:
                    logger.info(
                        f"Processing Batch {batch_num} ({len(batch)} chunks)... [Attempt {retry_count + 1}]"
                    )
                    response = self.client.embed(
                        model="nomic-embed-text",
                        input=batch,
                    )
                    all_embeddings.extend(response["embeddings"])
                    logger.info(f"Batch {batch_num} done")
                    batch_success = True
                    del response
                    gc.collect()
                except ollama.ResponseError as e:
                    retry_count += 1
                    logger.error(
                        f"Ollama ResponseError on Batch {batch_num} (Attempt {retry_count})"
                    )
                    if retry_count >= max_retries_per_batch:
                        raise OllamaException(
                            operation="embed_text",
                            detail=str(e),
                        )
                    logger.warning(f"Retrying batch {batch_num} after 3 second pause...")
                    time.sleep(3)

            del batch
            gc.collect()

        return all_embeddings


__all__ = ["OllamaService", "OllamaException"]
