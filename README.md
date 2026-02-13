# Danux

Self-hosted automation platform (IFTTT-like), focused on simple deployment and reliability.

## Step 4 status
This repository now includes base local infrastructure and service containers:
- API container (FastAPI skeleton)
- Worker container (queue consumer + webhook executor)
- PostgreSQL
- Redis

MVP API endpoints are available and the worker now consumes queued runs, executes webhook actions, retries with exponential backoff, and marks dead-letter after max attempts.

## Quickstart
1. Copy environment template:
   ```bash
   cp .env.example .env
   ```
2. Start services:
   ```bash
   docker compose up -d --build
   ```
3. Check service status:
   ```bash
   docker compose ps
   ```
4. Verify API healthcheck:
   ```bash
   curl -fsS http://localhost:8000/health
   ```
5. View logs (optional):
   ```bash
   docker compose logs --tail=100 api worker postgres redis
   ```

## Environment variables
See `.env.example` for all variables required by compose.

## Security notes
- Replace `POSTGRES_PASSWORD` and `APP_ENCRYPTION_KEY` before non-local use.
- Do not commit `.env` with real secrets.


## Step 4 quick verification
```bash
# 1) create workflow
curl -fsS -X POST http://localhost:8000/v1/workflows \
  -H "content-type: application/json" \
  -d '{"name":"demo","trigger_key":"demo_hook_01","action_url":"https://example.com/webhook"}'

# 2) trigger webhook
curl -fsS -X POST http://localhost:8000/v1/webhooks/demo_hook_01 \
  -H "content-type: application/json" \
  -H "x-idempotency-key: evt-001" \
  -d '{"hello":"world"}'

# 3) verify runs history
curl -fsS http://localhost:8000/v1/runs
```

6. Verify worker processed the queued run:
   ```bash
   curl -fsS http://localhost:8000/v1/runs
   ```
