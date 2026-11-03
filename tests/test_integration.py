import os
import psycopg2
import pytest
from fastapi.testclient import TestClient
from api import app

# Só roda se RUN_INTEGRATION=1 (CI seta; local não)
pytestmark = pytest.mark.skipif(
    not os.getenv("RUN_INTEGRATION"),
    reason="integração precisa de Postgres+Redis (CI seta RUN_INTEGRATION=1)",
)

client = TestClient(app)


def test_post_grava_no_banco(banco_pronto):
    url = "test-integration-1"
    resp = client.post("/bookmarks", json={"url": url})
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    bid = data["id"]

    # consulta direto no banco (não via API, pra provar persistência)
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT url, status FROM bookmarks WHERE id = %s", (bid,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    assert row is not None, f"bookmark {bid} não foi gravado"
    assert row[0] == url
    assert row[1] == "pending"
