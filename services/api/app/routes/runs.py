from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Run
from app.schemas import RunRead

router = APIRouter(prefix='/v1/runs', tags=['runs'])


@router.get('', response_model=list[RunRead])
def list_runs(
    workflow_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[Run]:
    stmt = select(Run).order_by(Run.id.desc()).limit(limit)
    if workflow_id is not None:
        stmt = stmt.where(Run.workflow_id == workflow_id)
    return list(db.scalars(stmt).all())
