import pytest
from app.services.rag_service import RAGService


def test_chunking_boundaries():
    sample_code = "\n".join([f"line_{i} = {i}" for i in range(1, 101)])
    chunks = RAGService.chunk_code_file(
        file_path="app/core.py",
        content=sample_code,
        project_id="test_proj",
        repository_id="test_repo",
        commit_sha="abcdef123456",
    )
    assert len(chunks) > 1
    # Check first chunk metadata
    first = chunks[0]
    assert first["metadata"]["file_path"] == "app/core.py"
    assert first["metadata"]["start_line"] == 1
    assert first["metadata"]["end_line"] == 40
    assert first["metadata"]["commit_sha"] == "abcdef123456"
