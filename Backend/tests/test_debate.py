import pytest
from httpx import AsyncClient
from app.main import create_app

@pytest.mark.asyncio
async def test_debate_endpoint():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {"topic": "Is AI beneficial?", "model_a": "A", "model_b": "B", "rounds": 2}
        r = await ac.post("/v1/debate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["topic"] == "Is AI beneficial?"
    assert len(data["transcript"]) == 4