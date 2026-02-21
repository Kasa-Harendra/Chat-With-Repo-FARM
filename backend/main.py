import sys
import os
from pathlib import Path

# Add project root to sys.path to allow absolute imports from 'backend'
root_path = str(Path(__file__).resolve().parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from backend.api import repo, chat, files
from backend.config import settings
from backend.utils.auth import create_session
import time
from backend.utils.logger_config import setup_logging

from backend.utils.limiter import limiter

# Initialize logging
logger = setup_logging()

app = FastAPI(title=settings.PROJECT_NAME)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Middleware
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        session_id = create_session()
        request.state.session_id = session_id
        response = await call_next(request)
        response.set_cookie(
            key="session_id", 
            value=session_id, 
            httponly=True, 
            samesite="lax",
            max_age=3600
        )
    else:
        request.state.session_id = session_id
        response = await call_next(request)
        
    return response

# Routes
app.include_router(repo.router, prefix="/api/repo", tags=["repo"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(files.router, prefix="/api/files", tags=["files"])

@app.get("/")
async def root():
    return {"message": "Welcome to ChatWithRepo API"}
