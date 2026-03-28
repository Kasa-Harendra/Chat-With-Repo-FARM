from pydantic import BaseModel
from typing import List, Dict, Optional, Union

class FileNode(BaseModel):
    name: str
    path: str
    summary: str
    dependencies: List[str] = []
    type: str
    isDir: bool = False

class DirectoryNode(BaseModel):
    name: str
    path: str
    summary: str
    file_count: int
    file_names: List[str]
    children: List[Union['FileNode', 'DirectoryNode']] = []
    isDir: bool = True

DirectoryNode.update_forward_refs()

class RepoTree(BaseModel):
    root: DirectoryNode
    session_id: str
