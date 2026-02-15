import psutil
import os
import gc
import logging

logger = logging.getLogger(__name__)

def log_memory(step_name):
    """Log current memory usage"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    mem_mb = mem_info.rss / 1024 / 1024  # RSS = Resident Set Size (actual RAM)
    
    logger.info(f"📊 MEMORY [{step_name}]: {mem_mb:.2f} MB")
    return mem_mb
