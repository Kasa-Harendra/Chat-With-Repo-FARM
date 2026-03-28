from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.services.rag_service import RAGService
from backend.services.tree_rag_service import TreeSearchService
from backend.services.cache_service import CacheService
from backend.utils.auth import get_session_id
from backend.utils.limiter import limiter
from langchain_ollama import ChatOllama
from backend.config import settings
import json
import asyncio
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ChatRequest(BaseModel):
    message: str

async def generate_response(prompt: str, context_files: list, cache_service: CacheService):
    llm = ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.CHAT_MODEL
    )
    
    context_text = "\n\n".join([f"File: {f['source']}\nContent:\n{f['content']}" for f in context_files])
    
    system_prompt = f"""You are a helpful assistant that answers questions about a code repository.
    Retrieved context contains the FULL CONTENT of the most relevant files based on their summaries.
    Use this context to provide accurate and detailed answers. Never halluciante. Just makeup your response from the context provided. 
    Keep the response readable and easy to understand in about 300 words in total.
    
    Context:
    {context_text}
    """
    
    full_prompt = f"{system_prompt}\n\nUser Question: {prompt}\nAnswer:"
    
    full_response = ""
    async for chunk in llm.astream(full_prompt):
        full_response += chunk.content
        yield f"data: {json.dumps({'content': chunk.content})}\n\n"
    
    # Cache the complete response
    cache_service.save_chat_response(prompt, context_text, full_response)

@router.post("")
@limiter.limit("30/minute")
async def chat(chat_request: ChatRequest, request: Request):
    session_id = get_session_id(request)
    if not session_id:
        raise HTTPException(status_code=400, detail="Session not initialized")
        
    rag_service = RAGService(session_id)
    tree_search = TreeSearchService(session_id)
    cache_service = CacheService(session_id)
    
    # Query for relevant files using Tree Search
    logger.info(f"Performing tree search for query: {chat_request.message}")
    context_files = await tree_search.query_tree(chat_request.message)
    
    repo_path = os.path.join(settings.DATA_PATH, session_id)
    
    if not os.path.exists(repo_path):
        logger.warning(f"Repository path {repo_path} not found for session {session_id}")
    else:
        # If Tree search found nothing or we want to fallback (keeping existing logic for now but context_files is already populated)
        if not context_files:
            logger.info("Tree search yielded no results, falling back to flat RAG summaries")
            summaries = rag_service.query(chat_request.message, k=3)
            for doc in summaries:
                source = doc.metadata.get("source")
                if not source:
                    continue
                file_path = os.path.join(repo_path, source)
                try:
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        context_files.append({
                            "source": source,
                            "content": content
                        })
                except Exception as e:
                    logger.error(f"Error reading context file {file_path}: {e}")
    
    context_text = "\n\n".join([f"File: {f['source']}\nContent:\n{f['content']}" for f in context_files])
    
    # Check Cache
    cached_response = cache_service.get_chat_response(chat_request.message, context_text)
    if cached_response:
        async def stream_cached():
            # Simulate streaming for the cached response
            for word in cached_response.split(' '):
                yield f"data: {json.dumps({'content': word + ' '})}\n\n"
                await asyncio.sleep(0.01)
        
        return StreamingResponse(stream_cached(), media_type="text/event-stream")
            
    return StreamingResponse(
        generate_response(chat_request.message, context_files, cache_service),
        media_type="text/event-stream"
    )
