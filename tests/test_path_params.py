from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_bookmark_id_invalido_retorna_422():
    resp = client.get("/bookmarks/abc")
    assert resp.status_code == 422
    body = resp.json()
    assert body["detail"][0]["type"] == "int_parsing"
    assert body["detail"][0]["loc"] == ["path", "bookmark_id"]
