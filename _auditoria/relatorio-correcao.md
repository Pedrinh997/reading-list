# Relatório de correção — reading-list

> Gerado em 2026-11-11 14:52:12
> HEAD: `e277fbb` — perf: escala de workers + nginx + métricas Prometheus (ver baseline_resumo.md)

---

## 1. Status dos gates do plano

| Fase | Item | Status |
|---|---|---|
| 2 | RAM livre ≥1500 MiB | ✅ 1669 MiB |
| 2 | Swap ≤100 MiB | ✅ 34 MiB |
| 3 | API healthy | ✅ |
| 4 | /metrics 200 | ✅ |
| 5 | nginx 8003 200 | ❌ (000?) |
| 5 | prometheus 9090 200 | ❌ (302) |
| 6 | sem SHA stray | ✅ |
| 6 | template removido | ✅ |
| 6 | seção Preparação | ✅ |

---

## 2. Configuração atual

```
NAME                    IMAGE                 COMMAND                  SERVICE   CREATED             STATUS                       PORTS
reading-list-api-1      reading-list-api      "uvicorn api:app --h…"   api       About an hour ago   Up About an hour (healthy)   0.0.0.0:8001->8000/tcp, [::]:8001->8000/tcp
reading-list-db-1       postgres:15           "docker-entrypoint.s…"   db        About an hour ago   Up About an hour (healthy)   0.0.0.0:5434->5432/tcp, [::]:5434->5432/tcp
reading-list-redis-1    redis:7-alpine        "docker-entrypoint.s…"   redis     About an hour ago   Up About an hour (healthy)   0.0.0.0:6380->6379/tcp, [::]:6380->6379/tcp
reading-list-worker-1   reading-list-worker   "rq worker --url red…"   worker    About an hour ago   Up About an hour             

workers: CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
sync:    off
RAM:     1.6Gi available  swap: 34Mi usado
```

---

## 3. Baseline oficial (não alterado)

```
# Baseline — reading-list (configuração final otimizada)

## Configuração
- uvicorn: 2 workers
- api.py: original (psycopg2.connect por request)
- postgres: synchronous_commit=off
- host: WSL2, 8 cores, 3.8 GiB RAM (com monitor_micro rodando em paralelo)

## Números (saturação 50 VUs, sem sleep, 70s)
- req/s: 267.3 (média de 2 runs: 267.42 / 267.13)
- p95: 244 ms (média de 2 runs: 243.4 / 244.6)
- p90: 219 ms
- avg: 147 ms
- max: 469 ms
- error rate: 0.00%
- checks: 100%

## Linha do tempo da otimização

| config | req/s | p95 |
```

---

## 4. Diff entregue pelo plano de correção

```
 .gitignore         | 11 +++++++++++
 Dockerfile.api     |  2 +-
 baseline_resumo.md | 35 +++++++++++++++++++++++++++++++++++
 nginx.conf         | 30 ++++++++++++++++++++++++++++++
 prometheus.yml     |  9 +++++++++
 5 files changed, 86 insertions(+), 1 deletion(-)
```
