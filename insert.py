import sys
import psycopg2
from redis import Redis
from rq import Queue
import jobs

# Aponta pro Postgres e Redis do COMPOSE (mapeados no host)
DATABASE_URL = "postgresql://reading:senha-forte-123@localhost:5434/readingdb"
REDIS_HOST = "localhost"
REDIS_PORT = 6380


def inserir_e_enfileirar(url: str) -> int:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bookmarks (url, title, status) VALUES (%s, NULL, 'pending') RETURNING id",
        (url,),
    )
    bookmark_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    print(f"bookmark inserido: id={bookmark_id}, url={url}, status=pending", flush=True)

    redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT)
    q = Queue("default", connection=redis_conn)
    job = q.enqueue(jobs.enriquecer_titulo, bookmark_id, url)
    print(f"job enfileirado: {job.id}", flush=True)
    return bookmark_id


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    inserir_e_enfileirar(url)
