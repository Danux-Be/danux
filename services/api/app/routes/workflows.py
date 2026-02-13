from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Workflow
from app.schemas import WorkflowCreate, WorkflowRead

router = APIRouter(prefix='/v1/workflows', tags=['workflows'])


@router.post('', response_model=WorkflowRead, status_code=status.HTTP_201_CREATED)
def create_workflow(payload: WorkflowCreate, db: Session = Depends(get_db)) -> Workflow:
    workflow = Workflow(
        name=payload.name,
        trigger_key=payload.trigger_key,
        action_url=str(payload.action_url),
        action_method=payload.action_method,
        action_headers=payload.action_headers,
        timeout_seconds=payload.timeout_seconds,
    )
    db.add(workflow)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='trigger_key already exists') from exc
    db.refresh(workflow)
    return workflow


@router.get('', response_model=list[WorkflowRead])
def list_workflows(db: Session = Depends(get_db)) -> list[Workflow]:
    return list(db.scalars(select(Workflow).order_by(Workflow.id.desc())).all())
