import hashlib
import json

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Run, Workflow
from app.schemas import TriggerAccepted
from app.services.queue import enqueue_run
from app.services.redaction import redact_headers

router = APIRouter(prefix='/v1/webhooks', tags=['webhooks'])


@router.post('/{trigger_key}', response_model=TriggerAccepted, status_code=status.HTTP_202_ACCEPTED)
async def receive_webhook(
    trigger_key: str,
    request: Request,
    db: Session = Depends(get_db),
    x_idempotency_key: str | None = Header(default=None),
) -> TriggerAccepted:
    workflow = db.scalar(select(Workflow).where(Workflow.trigger_key == trigger_key))
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='unknown trigger_key')

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='payload must be valid JSON')

    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='payload root must be a JSON object')

    raw_body = await request.body()
    idempotency_key = x_idempotency_key or hashlib.sha256(raw_body).hexdigest()

    incoming_headers = {k: v for k, v in request.headers.items()}
    run = Run(
        workflow_id=workflow.id,
        status='queued',
        idempotency_key=idempotency_key,
        trigger_payload=payload,
        trigger_headers=redact_headers(incoming_headers),
    )
    db.add(run)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing_run = db.scalar(
            select(Run).where(Run.workflow_id == workflow.id, Run.idempotency_key == idempotency_key)
        )
        if existing_run is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='duplicate event')
        return TriggerAccepted(run_id=existing_run.id, status=existing_run.status)

    db.refresh(run)
    enqueue_run({'run_id': run.id, 'workflow_id': workflow.id})
    return TriggerAccepted(run_id=run.id, status=run.status)
