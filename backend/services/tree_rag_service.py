import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from langchain_ollama import ChatOllama
from backend.config import settings
from backend.models.tree import FileNode, DirectoryNode, RepoTree
from backend.utils.languages import extension_map

logger = logging.getLogger(__name__)

class RepoTreeBuilder:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.repo_path = os.path.join(settings.DATA_PATH, session_id)
        self.tree_save_path = os.path.join(settings.DATA_PATH, "trees", f"{session_id}.json")
        os.makedirs(os.path.dirname(self.tree_save_path), exist_ok=True)
        
        self.summarizer_llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.SUMMARIZER_MODEL
        )

    async def build(self) -> RepoTree:
        """
        Recursively builds the tree by summarizing files and directories.
        """
        logger.info(f"Building tree for {self.repo_path}")
        root_node = await self._build_recursive(self.repo_path)
        tree = RepoTree(root=root_node, session_id=self.session_id)
        self.save_tree(tree)
        return tree

    async def _build_recursive(self, current_path: str) -> Union[FileNode, DirectoryNode]:
        name = os.path.basename(current_path)
        rel_path = os.path.relpath(current_path, self.repo_path)
        
        if os.path.isfile(current_path):
            with open(current_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            summary = await self.summarize_file(name, content)
            dependencies = self.extract_dependencies(content)
            ext = os.path.splitext(name)[1]
            
            return FileNode(
                name=name,
                path=rel_path,
                summary=summary,
                dependencies=dependencies,
                type=extension_map.get(ext, "unknown")
            )
        
        # Directory logic
        children = []
        for item in os.listdir(current_path):
            if item == '.git' or item == '__pycache__':
                continue
            item_path = os.path.join(current_path, item)
            child_node = await self._build_recursive(item_path)
            children.append(child_node)
        
        file_names = [c.name for c in children if not c.isDir]
        file_count = len([c for c in children if not c.isDir])
        
        summary = await self.summarize_directory(name, children)
        
        return DirectoryNode(
            name=name,
            path=rel_path,
            summary=summary,
            file_count=file_count,
            file_names=file_names,
            children=children
        )

    async def summarize_file(self, name: str, content: str) -> str:
        prompt = f"""Summarize the purpose and functionality of the file '{name}'.
        Be concise (2-3 sentences).
        
        Content:
        {content[:3000]}
        
        Summary:"""
        try:
            response = await self.summarizer_llm.ainvoke(prompt)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Error summarizing file {name}: {e}")
            return f"File node for {name}"

    async def summarize_directory(self, name: str, children: List[Union[FileNode, DirectoryNode]]) -> str:
        child_summaries = "\n".join([f"- {c.name}: {c.summary}" for c in children])
        prompt = f"""Summarize the directory '{name}' based on its contents:
        {child_summaries}
        
        Explain what this directory as a whole does. Be concise.
        
        Summary:"""
        try:
            response = await self.summarizer_llm.ainvoke(prompt)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Error summarizing directory {name}: {e}")
            return f"Directory node for {name}"

    def extract_dependencies(self, content: str) -> List[str]:
        # Simple heuristic for common languages. Can be enhanced with LLM.
        deps = []
        lines = content.split('\n')
        for line in lines[:50]: # Check first 50 lines for imports
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                deps.append(line)
        return deps

    def save_tree(self, tree: RepoTree):
        with open(self.tree_save_path, 'w', encoding='utf-8') as f:
            f.write(tree.json())
        logger.info(f"Tree saved to {self.tree_save_path}")

    def load_tree(self) -> Optional[RepoTree]:
        if os.path.exists(self.tree_save_path):
            with open(self.tree_save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return RepoTree(**data)
        return None

class TreeSearchService:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.repo_path = os.path.join(settings.DATA_PATH, session_id)
        self.builder = RepoTreeBuilder(session_id)
        self.searcher_llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.SEARCHER_MODEL
        )

    async def query_tree(self, user_query: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Navigates the tree to find relevant files, tracking the full path nodes.
        """
        tree = self.builder.load_tree()
        if not tree:
            logger.error(f"No tree found for session {self.session_id}")
            return []

        relevant_files = []
        # queue stores (node, current_depth, ancestor_nodes)
        queue = [(tree.root, 0, [])] 
        
        while queue:
            current_node, depth, ancestors = queue.pop(0)
            
            # Get dict representation but exclude 'children' to avoid recursive bloat in context
            node_dict = current_node.dict(exclude={"children"})
            current_path_list = ancestors + [node_dict]

            if depth >= max_depth:
                continue

            if not current_node.isDir:
                # If we've reached a file, return its content and the full path nodes leading to it
                relevant_files.append({
                    "source": current_node.path,
                    "content": self._read_file(current_node.path),
                    "path_nodes": ancestors # All ancestor directories
                })
                continue

            # Directory evaluation: Ask LLM which children are relevant
            picked_children = await self._evaluate_node(user_query, current_node)
            for child in current_node.children:
                if child.name in picked_children:
                    queue.append((child, depth + 1, current_path_list))
        
        return relevant_files

    async def _evaluate_node(self, query: str, node: DirectoryNode) -> List[str]:
        """
        Asks the LLM to pick relevant children names from a directory node.
        """
        options = "\n".join([f"- {c.name}: {c.summary}" for c in node.children])
        prompt = f"""Given the user query: "{query}"
        And the following files/directories in '{node.name}':
        {options}
        
        Pick the names of the MOST RELEVANT items to help answer the query.
        Return ONLY a comma-separated list of names. If none are relevant, return 'none'.
        
        Relevant items:"""
        
        try:
            response = await self.searcher_llm.ainvoke(prompt)
            result = response.content.strip().lower()
            if result == 'none':
                return []
            return [name.strip() for name in result.split(',')]
        except Exception as e:
            logger.error(f"Error evaluating node {node.name}: {e}")
            return []

    def _read_file(self, rel_path: str) -> str:
        full_path = os.path.join(self.repo_path, rel_path)
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return ""

from typing import Union
