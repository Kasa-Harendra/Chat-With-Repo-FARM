import sys
import os
from pathlib import Path

# Add project root to sys.path to allow absolute imports from 'backend'
root_path = str(Path(__file__).resolve().parent.parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

import shutil
import time
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

def cleanup_expired_sessions(max_age_seconds: int = 86400):
    """
    Deletes local directories and ChromaDB collections for sessions older than max_age_seconds.
    """
    now = time.time()
    
    # Cleanup data directory
    if os.path.exists(settings.DATA_PATH):
        for session_id in os.listdir(settings.DATA_PATH):
            if session_id == 'chroma':
                continue
            path = os.path.join(settings.DATA_PATH, session_id)
            if os.path.getmtime(path) < now - max_age_seconds:
                try:
                    shutil.rmtree(path)
                    logger.info(f"Cleaned up session data: {session_id}")
                except Exception as e:
                    logger.error(f"Failed to cleanup session {session_id}: {e}")
                    
    # Cleanup ChromaDB directory
    if os.path.exists(settings.CHROMA_DB_PATH):
        for session_id in os.listdir(settings.CHROMA_DB_PATH):
            path = os.path.join(settings.CHROMA_DB_PATH, session_id)
            if os.path.getmtime(path) < now - max_age_seconds:
                try:
                    shutil.rmtree(path)
                    logger.info(f"Cleaned up session ChromaDB: {session_id}")
                except Exception as e:
                    logger.error(f"Failed to cleanup ChromaDB {session_id}: {e}")

if __name__ == "__main__":
    # This could be run as a cron job or a separate background worker
    while True:
        cleanup_expired_sessions()
        time.sleep(86400) # Run every 24 hours
