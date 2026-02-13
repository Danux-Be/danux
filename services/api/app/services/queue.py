import json
from typing import Any

import redis

from app.config import settings

QUEUE_NAME = 'workflow_runs'


def enqueue_run(payload: dict[str, Any]) -> None:
    client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    client.rpush(QUEUE_NAME, json.dumps(payload))
