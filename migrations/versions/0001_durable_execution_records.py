"""Create versioned workflow and execution records.

Revision ID: 0001
Revises:
Create Date: 2026-10-07
"""

from __future__ import annotations

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workflow_definitions",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("workflow_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("tasks", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("revision > 0", name="ck_workflow_revision_positive"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workflow_id", "revision", name="uq_workflow_revision"),
    )
    op.create_index(
        op.f("ix_workflow_definitions_workflow_id"),
        "workflow_definitions",
        ["workflow_id"],
        unique=False,
    )
    op.create_table(
        "workflow_executions",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("workflow_definition_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'succeeded', 'failed')",
            name="ck_workflow_execution_status",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_definition_id"],
            ["workflow_definitions.id"],
            name="fk_workflow_execution_definition",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_workflow_executions_workflow_definition_id"),
        "workflow_executions",
        ["workflow_definition_id"],
        unique=False,
    )
    op.create_table(
        "task_executions",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("workflow_execution_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("task_name", sa.String(length=255), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "ordinal >= 0", name="ck_task_execution_ordinal_nonnegative"
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'succeeded', 'failed', 'blocked')",
            name="ck_task_execution_status",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_execution_id"],
            ["workflow_executions.id"],
            name="fk_task_execution_workflow_execution",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "workflow_execution_id", "task_name", name="uq_execution_task_name"
        ),
    )
    op.create_index(
        op.f("ix_task_executions_workflow_execution_id"),
        "task_executions",
        ["workflow_execution_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_task_executions_workflow_execution_id"), table_name="task_executions"
    )
    op.drop_table("task_executions")
    op.drop_index(
        op.f("ix_workflow_executions_workflow_definition_id"),
        table_name="workflow_executions",
    )
    op.drop_table("workflow_executions")
    op.drop_index(
        op.f("ix_workflow_definitions_workflow_id"), table_name="workflow_definitions"
    )
    op.drop_table("workflow_definitions")
