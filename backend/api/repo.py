from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Depends
from pydantic import BaseModel
from typing import List, Optional
from backend.services.repo_service import RepoService
from backend.services.rag_service import RAGService
from backend.utils.auth import get_session_id, create_session
from backend.utils.limiter import limiter
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# Global status tracking (For production, use Redis or a DB)
processing_status = {}

class RepoLoadRequest(BaseModel):
    url: str
    branch: Optional[str] = None

class RepoProcessRequest(BaseModel):
    selected_extensions: List[str]

@router.post("/load")
@limiter.limit("10/minute")
async def load_repo(repo_request: RepoLoadRequest, request: Request):
    session_id = get_session_id(request)
    if not session_id:
        raise HTTPException(status_code=400, detail="Session not initialized")
        
    logger.info(f"Loading repository: {repo_request.url} for session {session_id}")
    repo_service = RepoService(session_id)
    try:
        file_tree = repo_service.clone_repo(repo_request.url, repo_request.branch)
        processing_status[session_id] = "idle"
        return {"file_tree": file_tree}
    except Exception as e:
        logger.error(f"Failed to load repo {repo_request.url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def background_process_repo(session_id: str, extensions: List[str]):
    try:
        logger.info(f"Starting background processing for session {session_id}")
        processing_status[session_id] = "processing"
        repo_service = RepoService(session_id)
        rag_service = RAGService(session_id)
        
        # Clear existing collection for a fresh start
        rag_service.delete_collection()
        
        docs = repo_service.process_files(extensions)
        summaries = repo_service.generate_summaries(docs)
        rag_service.add_documents(summaries)
        
        processing_status[session_id] = "completed"
        logger.info(f"Successfully processed repo for session {session_id}")
    except Exception as e:
        processing_status[session_id] = "failed"
        logger.error(f"Background processing failed for session {session_id}: {e}")

@router.post("/process")
@limiter.limit("5/minute")
async def process_repo(process_request: RepoProcessRequest, background_tasks: BackgroundTasks, request: Request):
    session_id = get_session_id(request)
    if not session_id:
        raise HTTPException(status_code=400, detail="Session not initialized")
        
    logger.info(f"Queueing repository processing for session {session_id}")
    background_tasks.add_task(background_process_repo, session_id, process_request.selected_extensions)
    return {"status": "processing_started"}

@router.get("/status")
async def get_processing_status(request: Request):
    session_id = get_session_id(request)
    if not session_id:
        raise HTTPException(status_code=400, detail="Session not initialized")
    
    status = processing_status.get(session_id, "idle")
    return {"status": status}

@router.delete("/reset")
@limiter.limit("5/minute")
async def reset_session(request: Request):
    session_id = get_session_id(request)
    if not session_id:
        raise HTTPException(status_code=400, detail="Session not initialized")
        
    try:
        logger.info(f"Resetting session {session_id}")
        # Clear Vector DB
        rag_service = RAGService(session_id)
        rag_service.delete_collection()
        
        # Clear Local Repo
        repo_service = RepoService(session_id)
        repo_service.cleanup()
        
        # Reset Status
        processing_status[session_id] = "idle"
        
        logger.info(f"Session {session_id} reset successfully")
        return {"status": "success", "message": "Session data cleared"}
    except Exception as e:
        logger.error(f"Error resetting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
