import pytest
import os
import json
import asyncio
from unittest.mock import MagicMock, patch
from backend.services.tree_rag_service import RepoTreeBuilder
from backend.models.tree import RepoTree

@pytest.mark.asyncio
async def test_tree_builder_init():
    builder = RepoTreeBuilder("test_session")
    assert builder.session_id == "test_session"
    assert "test_session" in builder.repo_path

@pytest.mark.asyncio
async def test_extract_dependencies():
    builder = RepoTreeBuilder("test_session")
    content = "import os\nfrom typing import List\nprint('hello')"
    deps = builder.extract_dependencies(content)
    assert "import os" in deps
    assert "from typing import List" in deps

@patch('backend.services.tree_rag_service.ChatOllama')
@pytest.mark.asyncio
async def test_summarize_file(mock_ollama):
    mock_llm = MagicMock()
    # async invoke return mock
    future = asyncio.Future()
    future.set_result(MagicMock(content="Summary of file"))
    mock_llm.ainvoke.return_value = future
    
    mock_ollama.return_value = mock_llm
    
    builder = RepoTreeBuilder("test_session")
    summary = await builder.summarize_file("test.py", "print('test')")
    assert summary == "Summary of file"

@patch('backend.services.tree_rag_service.ChatOllama')
@pytest.mark.asyncio
async def test_summarize_directory(mock_ollama):
    mock_llm = MagicMock()
    future = asyncio.Future()
    future.set_result(MagicMock(content="Summary of directory"))
    mock_llm.ainvoke.return_value = future
    
    mock_ollama.return_value = mock_llm
    
    builder = RepoTreeBuilder("test_session")
    children = [] # Simplified for test
    summary = await builder.summarize_directory("root", children)
    assert summary == "Summary of directory"
