from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_url_como_numero_retorna_422():
    resp = client.post("/bookmarks", json={"url": 123})
    assert resp.status_code == 422
    body = resp.json()
    assert body["detail"][0]["loc"] == ["body", "url"]
    assert body["detail"][0]["type"] == "string_type"


def test_body_vazio_retorna_422():
    resp = client.post("/bookmarks", json={})
    assert resp.status_code == 422
    body = resp.json()
    assert body["detail"][0]["loc"] == ["body", "url"]
