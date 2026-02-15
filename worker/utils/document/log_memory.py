import logging
import os

import psutil

logger = logging.getLogger(__name__)


def log_memory(step_name: str) -> float:
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / 1024 / 1024
    logger.info(f"📊 MEMORY [{step_name}]: {mem_mb:.2f} MB")
    return mem_mb
