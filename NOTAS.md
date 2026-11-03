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

## Sessão 7 — CI/CD com GitHub Actions (concluída em 2026-11-02)

### Feito
- `git init` + `.gitignore` (.venv excluído)
- README com badge de CI
- 4 unit tests (sem Postgres/Redis): health, path params, body validation
- `pytest tests/ -v` → 4 passed local
- Repo público no GitHub
- `.github/workflows/ci.yml`: roda pytest em push/PR na main
- Testado: commit quebrado → CI vermelho + log visível
- Testado: fix → CI verde
- Badge no README atualizado automaticamente

### Aprendi
- CI roda em ambiente limpo (Ubuntu do GitHub), não no meu PC
- `pytest` local passando **não** garante CI passando (diferença de ambiente)
- Workflow dispara em push E PR, filtrando por branch
- `TestClient` do FastAPI permite testar sem subir servidor HTTP
- Testes que dependem de Postgres/Redis são integration tests (mais lentos, precisam de infra)
- Unit tests (lógica pura) rodam em qualquer CI sem infra
- GitHub Free: Actions ilimitado pra repos públicos

### Estado
- reading-list com 8 sessões completas (1, 2, 3, A, C, 4, 5, 6, 7)
- API HTTP + worker + Postgres + Redis + Docker Compose + CI
- Pronto pra: aplicar em projeto real, ou adicionar deploy (Railway)

### Próximos (opcionais)
- Deploy público (Railway): 2h, precisa conta
- Integration tests (com Postgres no CI via `services:`): 1h
- Aplicar o esqueleto em projeto real

## Sessão A — Integration test no CI (concluída em 2026-11-03)

### Feito
- `pytest.ini` com marker `integration`
- `tests/conftest.py` com fixture `banco_pronto`
- `tests/test_integration.py` (skipa local sem RUN_INTEGRATION=1)
- Workflow com `services: postgres + redis` + health-cmd
- Local: 4 passed, 1 skipped
- **CI: 5 passed com Postgres+Redis reais** ✅
- README de portfólio com diagrama ASCII + "o que aprendi"

### Aprendi
- CI sem infraestrutura só testa lógica pura
- `services:` do GitHub Actions sobe containers ao lado do job
- `health-cmd` previne race (Postgres pronto antes do pytest)
- Marker `integration` permite skip local, roda no CI
- Fixture `banco_pronto` cria tabela no CI (não tem init.sql automático)
- README com "o que aprendi" separa tutorial de projeto
