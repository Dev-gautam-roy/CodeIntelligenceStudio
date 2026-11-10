import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoints():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Code Intelligence Studio" in data["service"]

    v1_res = client.get("/api/v1/health")
    assert v1_res.status_code == 200


def test_prompt_generation_and_verification():
    # 1. Generate prompt
    gen_res = client.post(
        "/api/v1/prompts/generate",
        json={"category": "debugging", "target_context": {}},
    )
    assert gen_res.status_code == 200
    data = gen_res.json()
    assert "prompt_text" in data
    assert data["category"] == "debugging"

    # 2. Verify prompt
    ver_res = client.post(
        "/api/v1/prompts/verify",
        json={"prompt_text": data["prompt_text"], "token_budget": 4000},
    )
    assert ver_res.status_code == 200
    ver_data = ver_res.json()
    assert ver_data["valid"] is True
    assert ver_data["score"] >= 6.0


def test_agents_api_listing():
    res = client.get("/api/v1/agents")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 9
