from fastapi import Request, HTTPException
from backend.config import settings
import redis
import uuid

# Connect to Redis
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception:
    redis_client = None

def get_session_id(request: Request) -> str:
    # First check the request state (set by middleware)
    session_id = getattr(request.state, "session_id", None)
    if not session_id:
        # Fallback to cookie
        session_id = request.cookies.get("session_id")
    return session_id

def create_session() -> str:
    session_id = str(uuid.uuid4())
    if redis_client:
        try:
            redis_client.setex(f"session:{session_id}", 3600, "active") # 1 hour expiry
        except Exception:
            # Redis might be configured but not reachable
            pass
    return session_id
