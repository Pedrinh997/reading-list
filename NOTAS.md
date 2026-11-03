# Reading list

## Estado atual (Sessão C concluída)

### Stack
- Postgres 15 (container, :5434)
- Redis 7 (container, :6380)
- Worker rq (container, Dockerfile.worker)
- `insert.py` (host, venv, aponta pro compose)
- `jobs.py` (roda no worker, usa os.getenv pra ser portável)

### Fluxo
1. `python insert.py <url>` → INSERT pending + enfileira
2. Worker pega do Redis → GET + BeautifulSoup → UPDATE done ou failed
3. `retry_failed.py` re-enfileira failed (rq não retenta sozinho)

### Testado
- Happy path: title extraído, status=done
- URL inválida: status=failed
- `docker compose down` + `up`: dados preservados (volumes)
- 3 Postgres coexistem: :5432 CryptoPulse, :5433 nativo, :5434 compose
- Primeiro job em container: ~14s (cold start), próximos <1s

### Próximos passos (quando quiser)
- Sessão B: Fly.io deploy (precisa auth browser + cartão)
- Sessão A: GitHub Actions CI
- Sessão nova: FastAPI em vez de insert.py CLI
- Ou: parar aqui, aplicar em projeto real

## Sessão 5 — FastAPI (concluída em 2026-XX-XX)

### Feito
- `api.py` com FastAPI:
  - GET / → health
  - POST /bookmarks → INSERT pending + enfileira, retorna 201
  - GET /bookmarks/{id} → retorna estado atual, 404 se não existe
- Pydantic valida JSON automaticamente (BookmarkIn)
- response_model valida saída (BookmarkOut)
- Rodou em :8001 (CryptoPulse ocupa :8000)
- Testado: happy path, validação 422, 404

### Aprendi
- FastAPI: HTTP como função Python, validação automática
- POST retorna rápido porque worker processa em background
- Pydantic valida antes do código rodar (422 sem você escrever nada)
- raise HTTPException vira resposta HTTP
- App HTTP (uvicorn) e infra (compose) são camadas separadas
- O padrão do CryptoPulse: API enfileira, worker processa, GET lê

### Próximos
- Containerizar o uvicorn (Dockerfile.api) e colocar no compose
- Ou: CI/CD (pytest + GitHub Actions)
- Ou: deploy público (Railway, Render)
- Ou: parar e aplicar em projeto real
