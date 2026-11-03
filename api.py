import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue
import jobs

import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://reading:senha-forte-123@localhost:5434/readingdb",
)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6380"))

app = FastAPI(title="Reading List API")


class BookmarkIn(BaseModel):
    url: str


class BookmarkOut(BaseModel):
    id: int
    url: str
    title: str | None
    status: str


@app.get("/")
def root():
    return {"ok": True, "service": "reading-list"}


@app.post("/bookmarks", status_code=201)
def criar_bookmark(body: BookmarkIn):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bookmarks (url, status) VALUES (%s, 'pending') RETURNING id",
        (body.url,),
    )
    bookmark_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    q = Queue("default", connection=Redis(host=REDIS_HOST, port=REDIS_PORT))
    job = q.enqueue(jobs.enriquecer_titulo, bookmark_id, body.url)

    return {"id": bookmark_id, "status": "pending", "job_id": job.id}


@app.get("/bookmarks/{bookmark_id}", response_model=BookmarkOut)
def obter_bookmark(bookmark_id: int):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, url, title, status FROM bookmarks WHERE id = %s",
        (bookmark_id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="bookmark não encontrado")
    return {"id": row[0], "url": row[1], "title": row[2], "status": row[3]}
