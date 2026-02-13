from __future__ import annotations

import json
import logging
import time
from typing import Any

import redis
from sqlalchemy import text

from worker.config import settings
from worker.db import engine
from worker.executor import ExecutionError, execute_webhook_action
from worker.retry import compute_backoff

logger = logging.getLogger(__name__)
QUEUE_NAME = 'workflow_runs'


class WorkerJobs:
    def __init__(self) -> None:
        self.redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    def poll_once(self, timeout_seconds: int = 1) -> bool:
        item = self.redis.blpop(QUEUE_NAME, timeout=timeout_seconds)
        if item is None:
            return False

        _, raw_payload = item
        payload = self._decode_job(raw_payload)
        run_id = int(payload['run_id'])
        self.process_run(run_id)
        return True

    def _decode_job(self, raw_payload: str) -> dict[str, Any]:
        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError as exc:
            raise ValueError('invalid job payload') from exc
        if not isinstance(payload, dict) or 'run_id' not in payload:
            raise ValueError('job payload missing run_id')
        return payload

    def process_run(self, run_id: int) -> None:
        run = self._get_run_and_workflow(run_id)
        if run is None:
            logger.warning('run not found', extra={'run_id': run_id})
            return
        if run['status'] not in {'queued', 'retrying'}:
            logger.info('run already processed, skipping', extra={'run_id': run_id, 'status': run['status']})
            return

        self._update_run_status(run_id, 'running', None)

        attempt = 1
        while attempt <= settings.max_attempts:
            try:
                status_code = execute_webhook_action(
                    action_url=run['action_url'],
                    action_method=run['action_method'],
                    action_headers=run['action_headers'] or {},
                    payload=run['trigger_payload'] or {},
                    timeout_seconds=run['timeout_seconds'],
                )
                self._update_run_status(run_id, 'succeeded', None)
                logger.info('run succeeded', extra={'run_id': run_id, 'status_code': status_code})
                return
            except ExecutionError as exc:
                is_last_attempt = attempt >= settings.max_attempts
                if is_last_attempt:
                    self._update_run_status(run_id, 'dead_letter', str(exc))
                    logger.error('run moved to dead-letter', extra={'run_id': run_id, 'error': str(exc)})
                    return

                self._update_run_status(run_id, 'retrying', str(exc))
                backoff = compute_backoff(
                    attempt=attempt,
                    base_seconds=settings.backoff_base_seconds,
                    max_seconds=settings.backoff_max_seconds,
                )
                logger.warning('run retry scheduled', extra={'run_id': run_id, 'attempt': attempt, 'delay': backoff})
                time.sleep(backoff)
                attempt += 1

    def _get_run_and_workflow(self, run_id: int) -> dict[str, Any] | None:
        query = text(
            """
            SELECT
              r.id,
              r.status,
              r.trigger_payload,
              w.action_url,
              w.action_method,
              w.action_headers,
              w.timeout_seconds
            FROM runs r
            JOIN workflows w ON w.id = r.workflow_id
            WHERE r.id = :run_id
            """
        )
        with engine.begin() as conn:
            row = conn.execute(query, {'run_id': run_id}).mappings().first()
            return dict(row) if row else None

    def _update_run_status(self, run_id: int, status: str, error_message: str | None) -> None:
        statement = text(
            """
            UPDATE runs
            SET status = :status,
                error_message = :error_message,
                updated_at = NOW()
            WHERE id = :run_id
            """
        )
        with engine.begin() as conn:
            conn.execute(statement, {'run_id': run_id, 'status': status, 'error_message': error_message})
