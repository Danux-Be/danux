from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Workflow(Base):
    __tablename__ = 'workflows'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    action_url: Mapped[str] = mapped_column(Text, nullable=False)
    action_method: Mapped[str] = mapped_column(String(8), nullable=False, default='POST')
    action_headers: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    runs: Mapped[list[Run]] = relationship(back_populates='workflow')


class Run(Base):
    __tablename__ = 'runs'
    __table_args__ = (UniqueConstraint('workflow_id', 'idempotency_key', name='uq_runs_workflow_idempotency'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey('workflows.id', ondelete='CASCADE'), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default='queued')
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    trigger_headers: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    workflow: Mapped[Workflow] = relationship(back_populates='runs')
