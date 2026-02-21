from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from backend.services.embedding_service import get_embedding_function
from backend.config import settings
from typing import List, Optional
import os
import shutil
import gc
import time
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.db_path = os.path.join(settings.CHROMA_DB_PATH, session_id)
        self.embedding_fn = get_embedding_function()

    def add_documents(self, documents: List[Document]):
        """
        Add documents to ChromaDB for the given session.
        """
        db = Chroma.from_documents(
            documents=documents,
            embedding=self.embedding_fn,
            persist_directory=self.db_path
        )
        # In newer versions of langchain-chroma/chromadb, persist() is often automatic or handled by the client.
        # But we call it for safety.
        try:
            db.persist()
        except AttributeError:
            pass # Method might not exist in all versions
        
        # Explicitly clear the object to help Windows release file handles
        db = None
        gc.collect()

    def query(self, query_text: str, k: int = 5) -> List[Document]:
        """
        Perform similarity search.
        """
        if not os.path.exists(self.db_path):
            return []
            
        db = Chroma(
            persist_directory=self.db_path,
            embedding_function=self.embedding_fn
        )
        results = db.similarity_search(query_text, k=k)
        
        # Explicitly clear the object to help Windows release file handles
        db = None
        gc.collect()
        
        return results

    def delete_collection(self):
        """
        Cleanup ChromaDB for the session.
        Handles Windows file locking issues with retries and garbage collection.
        """
        if not os.path.exists(self.db_path):
            return

        # Force GC to release any dangling ChromaDB/SQLite handles
        gc.collect()
        time.sleep(0.5) # Give OS a moment to catch up

        def handle_remove_read_only(func, path, exc):
            import stat
            if not os.access(path, os.W_OK):
                os.chmod(path, stat.S_IWUSR)
                func(path)
            else:
                # If it's still failing (likely a lock), we log it and wait
                logger.warning(f"File still locked: {path}. Retry might be needed.")

        max_retries = 3
        for i in range(max_retries):
            try:
                shutil.rmtree(self.db_path, onerror=handle_remove_read_only)
                logger.info(f"Successfully deleted ChromaDB collection for session {self.session_id}")
                return
            except Exception as e:
                if i < max_retries - 1:
                    logger.warning(f"Retry {i+1} for deleting {self.db_path}: {e}")
                    gc.collect()
                    time.sleep(1) # Wait longer between retries
                else:
                    logger.error(f"Failed to delete ChromaDB after {max_retries} attempts: {e}")
                    raise e
