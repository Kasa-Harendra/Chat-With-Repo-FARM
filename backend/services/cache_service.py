import hashlib
import json
from backend.utils.auth import redis_client
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.prefix = f"cache:{session_id}:"
        self.expiry = 3600 * 24  # 24 hours for chat cache

    def _generate_key(self, prompt: str, context: str) -> str:
        # Create a unique key based on prompt and the retrieved context
        data = f"{prompt}:{context}"
        hash_val = hashlib.md5(data.encode()).hexdigest()
        return f"{self.prefix}{hash_val}"

    def get_chat_response(self, prompt: str, context: str) -> str:
        if not redis_client:
            return None
        
        key = self._generate_key(prompt, context)
        try:
            cached = redis_client.get(key)
            if cached:
                logger.info(f"Cache hit for session {self.session_id}")
                return cached
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        return None

    def save_chat_response(self, prompt: str, context: str, response: str):
        if not redis_client:
            return
            
        key = self._generate_key(prompt, context)
        try:
            redis_client.setex(key, self.expiry, response)
            logger.info(f"Cached response for session {self.session_id}")
        except Exception as e:
            logger.error(f"Redis set error: {e}")
