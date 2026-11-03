import os
import psycopg2
import pytest


@pytest.fixture
def banco_pronto():
    """Garante que a tabela bookmarks existe. Só roda se DATABASE_URL estiver setada."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL não setada")

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
          id SERIAL PRIMARY KEY,
          url TEXT NOT NULL,
          title TEXT,
          status TEXT NOT NULL DEFAULT 'pending'
            CHECK (status IN ('pending', 'processing', 'done', 'failed')),
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

    yield

    # cleanup: apaga só os criados pelo teste
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("DELETE FROM bookmarks WHERE url LIKE 'test-%'")
    conn.commit()
    cur.close()
    conn.close()
