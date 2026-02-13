# Step 4 — MVP API + Worker Contracts

## Endpoints

### Health
- `GET /health`
- Returns: `200 {"status":"ok"}`

### Workflows
- `POST /v1/workflows`
  - Body:
    - `name` (string)
    - `trigger_key` (6-128 chars, `[a-zA-Z0-9_-]`)
    - `action_url` (http/https URL)
    - `action_method` (`POST|PUT|PATCH`, optional, default `POST`)
    - `action_headers` (object, optional)
    - `timeout_seconds` (1-30, optional, default 10)
  - Returns: `201` workflow object
  - Returns: `409` if `trigger_key` already exists

- `GET /v1/workflows`
  - Returns: `200` list of workflows

### Webhook Trigger
- `POST /v1/webhooks/{trigger_key}`
  - Headers:
    - Optional `X-Idempotency-Key`
  - Body:
    - JSON object only
  - Behavior:
    - Creates a queued run.
    - Redacts sensitive incoming headers before persistence.
    - Enqueues `{run_id, workflow_id}` into Redis list `workflow_runs`.
  - Returns:
    - `202 {run_id, status}`
    - `404` unknown trigger key
    - `400` invalid JSON/non-object payload

### Runs History
- `GET /v1/runs?workflow_id=<id>&limit=<1..200>`
  - Returns: `200` list of runs, newest first

## Security and data handling
- Sensitive inbound headers are redacted before being saved with run records.
- Idempotency is enforced per workflow (`workflow_id + idempotency_key` unique).
- This step does not yet implement webhook signature validation (planned next).


## Worker execution lifecycle (Step 4)
- Queue: Redis list `workflow_runs` (payload includes `run_id`).
- Status flow: `queued` -> `running` -> `succeeded` or `retrying` -> `dead_letter`.
- Retries: exponential backoff with env-configurable limits (`WORKER_MAX_ATTEMPTS`, `WORKER_BACKOFF_*`).
