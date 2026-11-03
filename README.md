# Reading List

API de bookmarks com **enriquecimento assíncrono**. Você manda uma URL, ela é
salva imediatamente (`pending`), e em background o worker extrai o `<title>`
da página e atualiza o banco (`done`).

**Demo interativo:** rode `docker compose up -d`, abra `http://localhost:8001/docs`.

## Como funciona

```
cliente ──POST /bookmarks──▶ API ──INSERT pending──▶ Postgres
                              │
                              └──enqueue──▶ Redis ──▶ worker
                                                        │
                                                        ├─GET url
                                                        ├─BeautifulSoup
                                                        └─UPDATE done ──▶ Postgres
```

- API responde em **<100ms** (INSERT + enqueue)
- Worker leva 1-5s (GET externo + parse)
- Desacoplado: cliente não espera o worker

## Stack

- **FastAPI** — HTTP, validação via Pydantic
- **Postgres** — persistência, `status` (`pending`/`processing`/`done`/`failed`)
- **Redis + rq** — fila, worker stateless
- **Docker Compose** — 4 serviços (`db`, `redis`, `api`, `worker`)
- **GitHub Actions** — CI com unit + integration tests (Postgres+Redis como `services`)

## Rodar

```bash
docker compose up -d && sleep 20
curl -X POST http://localhost:8001/bookmarks \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
# {"id":1,"status":"pending","job_id":"..."}

sleep 5
curl http://localhost:8001/bookmarks/1
# {"id":1,...,"title":"Example Domain","status":"done"}
```

Docs: `http://localhost:8001/docs`

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | health |
| `POST` | `/bookmarks` | cria bookmark (`pending`) + enfileira |
| `GET` | `/bookmarks/{id}` | estado atual |

## Testes

```bash
pip install -r requirements.txt
pytest tests/ -v
# 4 passed, 1 skipped (integration skipa local)
```

- **Unit** (sempre, sem infra): 4 testes
- **Integration** (`RUN_INTEGRATION=1` + Postgres+Redis): prova que `POST` grava no banco

## Status

![CI](https://github.com/Pedrinh997/reading-list/actions/workflows/ci.yml/badge.svg)

## O que aprendi

- **Fila ≠ banco.** Redis guarda o job, Postgres guarda o dado.
- **`POST` rápido é feature.** Aceitar o trabalho e fazer o trabalho são camadas separadas.
- **Pydantic valida sem código.** `BookmarkIn` rejeita `{"url": 123}` com 422 antes do meu código rodar.
- **Volume sobrevive.** `docker compose down` mata container, preserva volume.
- **`localhost` dentro do container não é o host.** `os.getenv("DATABASE_URL")` — mesmo código, contexto diferente.
- **CI verde ≠ "funciona no meu PC".** Ambiente limpo, `pip install` do zero.
- **Worker ocioso ≠ worker quebrado.** Silêncio é `BLPOP`. O indicador é a fila.

## Licença

MIT
