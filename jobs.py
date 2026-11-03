import os
import psycopg2
import requests
from bs4 import BeautifulSoup

# Lê do ambiente (container) ou usa localhost:5433 (host/venv)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://reading:senha-forte-123@localhost:5433/readingdb",
)


def _update_status(bookmark_id: int, status: str, title: str | None = None):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    if title is None:
        cur.execute(
            "UPDATE bookmarks SET status = %s WHERE id = %s",
            (status, bookmark_id),
        )
    else:
        cur.execute(
            "UPDATE bookmarks SET status = %s, title = %s WHERE id = %s",
            (status, title, bookmark_id),
        )
    conn.commit()
    linhas = cur.rowcount
    cur.close()
    conn.close()
    return linhas


def enriquecer_titulo(bookmark_id: int, url: str) -> str:
    print(f"[{os.getpid()}] buscando {url}", flush=True)
    _update_status(bookmark_id, "processing")
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        titulo = soup.title.string.strip() if soup.title and soup.title.string else "(sem titulo)"
        print(f"[{os.getpid()}] titulo extraido: {titulo!r}", flush=True)
        linhas = _update_status(bookmark_id, "done", titulo)
        print(f"[{os.getpid()}] banco atualizado: done ({linhas} linha)", flush=True)
        return titulo
    except Exception as e:
        print(f"[{os.getpid()}] erro: {e}", flush=True)
        _update_status(bookmark_id, "failed")
        raise
