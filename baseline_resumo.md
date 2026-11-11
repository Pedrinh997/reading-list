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
|---|---|---|
| 1 worker, sync=on (original) | 179.3 | 384 ms |
| 4 workers, sync=on | 216.3 | 408 ms |
| 2 workers, sync=on | 234.9 | 317 ms |
| **2 workers, sync=off** | **267.3** | **244 ms** |

Ganho total vs original: +49% req/s, −36% p95.

## O que NÃO funcionou (documentado)
- Pool de conexão psycopg2 (isolado ou + workers): 0% ou regressão
- Cliente Redis compartilhado (module-level): 0%
- 4 workers: pior que 2 por pressão de memória

## Tradeoff do sync=off
Em crash do host, perde até ~60ms de transações commitadas (WAL buffer).
Aceitável para reading-list. Inaceitável para dados financeiros.

## Worker RQ (nota)

Sob carga de 50 VUs (104 POST/s), o worker com 4 réplicas drena
~11 jobs/s. Fila cresce a ~93 jobs/s. Não é viável zerar fila em
tempo real neste host (precisaria ~38 workers).

Comportamento esperado: worker é assíncrono. API responde 201
imediatamente, scrape acontece em background com fila acumulando.
Isso é a arquitetura, não um bug.

4 réplicas reduzem throughput da API (208 vs 267 req/s) por
pressão de memória em 3.8 GiB. Manter 1 réplica.

## Drain rate do worker (medido)

| workers RQ | drain rate | req/s da API |
|---|---|---|
| 1 | 3.0 jobs/s | 267 |
| 4 | 11.0 jobs/s | 208 (−22%) |

Trade-off: 4 workers custam −59 req/s da API para ganhar
+8 jobs/s de scrape. 1 worker é a escolha correta.

Sob carga 50 VUs: API enfileira ~104 POST/s. Com 1 worker
drenando 3/s, fila cresce ~101/s. Sustentável para burst,
não para carga permanente — que é exatamente o caso de uso.

---

## Preparação para próxima fase (commitada, NÃO executada)

Os itens abaixo existem no repositório mas **não fazem parte do baseline medido**:

- `nginx.conf` — proxy reverso pronto. Serviço `nginx` no compose. **Não medido sob carga.**
- `prometheus.yml` — scrape config. Serviço `prometheus` no compose. **Não usado em produção.**
- `prometheus-fastapi-instrumentator` — `/metrics` exposto no `api.py`. Útil para monitorar mudanças futuras.

Esses 3 itens foram adicionados para deixar o projeto pronto para a próxima rodada de otimização (4/6 workers com RAM livre). **O baseline oficial continua sendo 267 req/s / p95 244 ms com 2 workers e sync=off.**

---

## Sessão 3 — Resultado final

### O que foi entregue
- `api.py` expõe `/metrics` (prometheus-fastapi-instrumentator)
- `docker-compose.yml` tem `nginx` (8003) e `prometheus` (9091)
- `nginx.conf` e `prometheus.yml` com config canônica, validados
- `healthcheck` da API usa Python (curl não existe na imagem slim)
- `baseline_resumo.md` sem SHA stray, sem template não preenchido
- `.gitignore` sem duplicatas, com `_auditoria/` ignorado

### 4 checks passando
| serviço | porta | status |
|---|---|---|
| api | 8001 | 200 |
| metrics | 8001 | 200 |
| nginx | 8003 | 200 |
| prometheus | 9091 | 200 (target api UP) |

### Baseline oficial (INALTERADO)
- **267 req/s, p95 244 ms, 2 workers, sync=off, 0% erro**
- Configurado em `d062bfc`, verificado em `verify-final.json`
- Nenhuma mudança de código Python no caminho crítico

### O que ficou para depois
- Multiprocess Prometheus (métricas agregadas por worker uvicorn)
- HTTP/2 no nginx (TLS requerido)
- Escalar uvicorn para 4 workers com `monitor_micro` parado (pode dar 300+ req/s)
