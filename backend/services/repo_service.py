import os
import shutil
import git
import time
from typing import List, Dict, Any, Optional
from backend.config import settings
from backend.utils.languages import extension_map
from backend.utils.notebook_parser import parse_notebook
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
import logging

logger = logging.getLogger(__name__)

class RepoService:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.repo_path = os.path.join(settings.DATA_PATH, session_id)
        self.llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.CHAT_MODEL
        )

    def clone_repo(self, url: str, branch: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Clones the repository and returns the file tree.
        """
        if os.path.exists(self.repo_path):
            def handle_remove_read_only(func, path, exc):
                import stat
                if not os.access(path, os.W_OK):
                    os.chmod(path, stat.S_IWUSR)
                    func(path)
                else:
                    raise
            
            try:
                # shutil.rmtree(self.repo_path, onerror=handle_remove_read_only)
                ...
            except Exception as e:
                logger.error(f"Failed to delete existing repo path: {e}")
                # Try simple rename as last resort
                old_path = f"{self.repo_path}_{int(time.time())}"
                try:
                    os.rename(self.repo_path, old_path)
                except Exception as rename_error:
                    logger.error(f"Failed to rename repo path: {rename_error}")
                    raise Exception(f"Could not clear directory {self.repo_path}. Please delete it manually.")
            
        try:
            clone_args = {}
            if branch:
                clone_args["branch"] = branch
                
            repo = git.Repo.clone_from(url, self.repo_path, **clone_args)
            return self._get_file_tree(self.repo_path)
        except Exception as e:
            logger.error(f"Failed to clone repo: {e}")
            raise Exception(f"Cloning failed: {str(e)}")

    def _get_file_tree(self, path: str) -> List[Dict[str, Any]]:
        tree = []
        for item in os.listdir(path):
            if item == '.git':
                continue
            item_path = os.path.join(path, item)
            is_dir = os.path.isdir(item_path)
            
            node = {
                "name": item,
                "path": os.path.relpath(item_path, self.repo_path),
                "isDir": is_dir
            }
            
            if is_dir:
                node["children"] = self._get_file_tree(item_path)
            else:
                ext = os.path.splitext(item)[1]
                node["type"] = extension_map.get(ext, "unknown")
                
            tree.append(node)
        return tree

    def process_files(self, selected_extensions: List[str]) -> List[Document]:
        """
        Processes files, filters by extension, and returns list of Documents.
        """
        documents = []
        for root, dirs, files in os.walk(self.repo_path):
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext not in selected_extensions:
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    if ext == '.ipynb':
                        content = parse_notebook(content)
                        
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": os.path.relpath(file_path, self.repo_path),
                            "extension": ext
                        }
                    )
                    documents.append(doc)
                except Exception as e:
                    logger.warning(f"Could not read file {file_path}: {e}")
                    
        return documents

    def generate_summaries(self, documents: List[Document]) -> List[Document]:
        """
        Generates a BRIEF summary for each document using OLLAMA.
        """
        summarized_docs = []
        for doc in documents:
            source = doc.metadata.get("source", "unknown")
            logger.info(f"Generating summary for {source}...")
            
            prompt = f"""Summarize the following code/file content in 3-4 BRIEF sentences. 
            Focus on its purpose and main functionality within the repository.
            
            Content:
            {doc.page_content[:2000]} # Limit content to avoid context overflow
            
            Summary:"""
            
            try:
                response = self.llm.invoke(prompt)
                summary = response.content.strip()
                
                summarized_docs.append(Document(
                    page_content=summary,
                    metadata=doc.metadata
                ))
            except Exception as e:
                logger.error(f"Failed to summarize {source}: {e}")
                # Fallback to a generic summary if LLM fails
                summarized_docs.append(Document(
                    page_content=f"Source code file: {source}",
                    metadata=doc.metadata
                ))
                
        return summarized_docs

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        return splitter.split_documents(documents)

    def cleanup(self):
        if os.path.exists(self.repo_path):
            def handle_remove_read_only(func, path, exc):
                import stat
                if not os.access(path, os.W_OK):
                    os.chmod(path, stat.S_IWUSR)
                    func(path)
                else:
                    raise
            
            try:
                shutil.rmtree(self.repo_path, onerror=handle_remove_read_only)
            except Exception as e:
                logger.error(f"Failed to cleanup repo path: {e}")
