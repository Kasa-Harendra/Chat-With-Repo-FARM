from langchain_ollama import OllamaEmbeddings
from backend.config import settings

def get_embedding_function():
    return OllamaEmbeddings(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.EMBEDDING_MODEL
    )
