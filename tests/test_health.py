from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_root_responde():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["service"] == "reading-list"
