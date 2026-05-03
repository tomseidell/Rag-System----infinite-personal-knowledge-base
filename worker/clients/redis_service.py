import json
import logging
import os

import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

_STATUS_TTL = 60 * 60 * 24 # 1 day


class RedisService:
    def __init__(self):
        self.client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

    def set_status(self, document_id: int, step: str, message: str = "") -> None:
        try:
            self.client.setex(
                f"document:status:{document_id}",
                _STATUS_TTL,
                json.dumps({"step": step, "message": message}),
            )
        except RedisError:
            logger.warning(f"Failed to set status for document {document_id}", exc_info=True)
