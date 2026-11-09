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
d062bfc5d1d33e9e205e3ba6cd5ffa7f47bb11d4
