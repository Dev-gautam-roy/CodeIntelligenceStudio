import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.repository import Repository

client = TestClient(app)


def test_codebase_file_tree_and_content():
    db = SessionLocal()
    repo = db.query(Repository).first()
    db.close()
    if not repo:
        pytest.skip("No repositories in DB to test")

    # Test file tree
    res = client.get(f"/api/v1/repositories/{repo.id}/file-tree")
    assert res.status_code == 200
    tree = res.json()
    assert isinstance(tree, list)

    # Test chat
    chat_res = client.post(
        f"/api/v1/repositories/{repo.id}/chat",
        json={"message": "What is the main function or entrypoint?", "history": []},
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert "reply" in chat_data
    assert "references" in chat_data
    assert "model_used" in chat_data
