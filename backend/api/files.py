from fastapi import APIRouter, Request, HTTPException
import os
from backend.config import settings
from backend.utils.auth import get_session_id
from backend.utils.languages import extension_map
from backend.utils.limiter import limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("")
@limiter.limit("60/minute")
async def get_file_content(path: str, request: Request):
    session_id = get_session_id(request)
    if not session_id:
        raise HTTPException(status_code=400, detail="Session not initialized")
        
    repo_path = os.path.join(settings.DATA_PATH, session_id)
    full_path = os.path.join(repo_path, path)
    
    # Security check: ensure path is within the session's repo directory
    if not os.path.abspath(full_path).startswith(os.path.abspath(repo_path)):
        logger.warning(f"Path traversal attempt by session {session_id}: {path}")
        raise HTTPException(status_code=403, detail="Forbidden")
        
    if not os.path.exists(full_path) or os.path.isdir(full_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        ext = os.path.splitext(full_path)[1]
        language = extension_map.get(ext, "text")
        
        logger.debug(f"Retrieved content for: {path} (Session: {session_id})")
        return {
            "content": content,
            "language": language,
            "path": path
        }
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
