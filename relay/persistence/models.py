"""SQLAlchemy records for versioned definitions and durable execution state."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid


class Base(DeclarativeBase):
    """Base metadata for Relay's durable database records."""


# v0.2 persistence tables are deliberately limited to definitions and runs.
class WorkflowDefinitionRecord(Base):
    """One immutable revision of a workflow's JSON-compatible definition."""

    __tablename__ = "workflow_definitions"
    __table_args__ = (
        UniqueConstraint("workflow_id", "revision", name="uq_workflow_revision"),
        CheckConstraint("revision > 0", name="ck_workflow_revision_positive"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tasks: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    executions: Mapped[list[WorkflowExecutionRecord]] = relationship(
        back_populates="definition"
    )


class WorkflowExecutionRecord(Base):
    """One durable run pinned to a specific workflow definition revision."""

    __tablename__ = "workflow_executions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'succeeded', 'failed')",
            name="ck_workflow_execution_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    workflow_definition_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "workflow_definitions.id",
            name="fk_workflow_execution_definition",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    definition: Mapped[WorkflowDefinitionRecord] = relationship(
        back_populates="executions"
    )
    task_executions: Mapped[list[TaskExecutionRecord]] = relationship(
        back_populates="workflow_execution",
        cascade="all, delete-orphan",
        order_by="TaskExecutionRecord.ordinal",
    )


class TaskExecutionRecord(Base):
    """Durable state and outcome for one task within a workflow execution."""

    __tablename__ = "task_executions"
    __table_args__ = (
        UniqueConstraint(
            "workflow_execution_id", "task_name", name="uq_execution_task_name"
        ),
        CheckConstraint("ordinal >= 0", name="ck_task_execution_ordinal_nonnegative"),
        CheckConstraint(
            "status IN ('pending', 'running', 'succeeded', 'failed', 'blocked')",
            name="ck_task_execution_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    workflow_execution_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "workflow_executions.id",
            name="fk_task_execution_workflow_execution",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    result: Mapped[Any | None] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    workflow_execution: Mapped[WorkflowExecutionRecord] = relationship(
        back_populates="task_executions"
    )
