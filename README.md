# Reading List

Bookmarks com enriquecimento assíncrono: API recebe URL, worker extrai o
`<title>` da página e atualiza o banco.

## Stack

- **FastAPI** — API HTTP (`api.py`)
- **Postgres** — persistência (container `db`)
- **Redis + rq** — fila (`worker`)
- **Docker Compose** — 4 serviços (db, redis, api, worker)

## Rodar

    docker compose up -d
    curl -X POST http://localhost:8001/bookmarks \
      -H "Content-Type: application/json" \
      -d '{"url": "https://example.com"}'

## Endpoints

- `GET /` — health
- `POST /bookmarks` — cria bookmark (`pending`) e enfileira job
- `GET /bookmarks/{id}` — retorna estado atual

## Status

![CI](https://github.com/SEU_USUARIO/reading-list/actions/workflows/ci.yml/badge.svg)
