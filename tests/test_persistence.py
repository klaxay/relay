"""Tests for Relay's durable SQLAlchemy record mappings."""

from __future__ import annotations

from datetime import datetime, timezone
import unittest
from uuid import uuid4

from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from relay.persistence.models import (
    Base,
    TaskExecutionRecord,
    WorkflowDefinitionRecord,
    WorkflowExecutionRecord,
)


class PersistenceModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")

        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _record) -> None:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_records_round_trip_json_and_preserve_task_declaration_order(self) -> None:
        definition = WorkflowDefinitionRecord(
            workflow_id=uuid4(),
            revision=1,
            name="example",
            tasks=[
                {"name": "prepare", "dependencies": [], "input": {"enabled": True}},
                {"name": "publish", "dependencies": ["prepare"], "input": "ready"},
            ],
        )
        execution = WorkflowExecutionRecord(
            definition=definition,
            status="succeeded",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            task_executions=[
                TaskExecutionRecord(
                    task_name="publish",
                    ordinal=1,
                    status="succeeded",
                    result={"published": True},
                ),
                TaskExecutionRecord(
                    task_name="prepare",
                    ordinal=0,
                    status="succeeded",
                    result=["ready"],
                ),
            ],
        )
        self.session.add(execution)
        self.session.commit()
        self.session.expire_all()

        loaded = self.session.get(WorkflowExecutionRecord, execution.id)
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.definition.revision, 1)
        self.assertEqual(loaded.definition.tasks[0]["input"], {"enabled": True})
        self.assertEqual(
            [task.task_name for task in loaded.task_executions], ["prepare", "publish"]
        )
        self.assertEqual(loaded.task_executions[1].result, {"published": True})

    def test_workflow_revision_is_unique_per_workflow(self) -> None:
        workflow_id = uuid4()
        self.session.add_all(
            [
                WorkflowDefinitionRecord(
                    workflow_id=workflow_id,
                    revision=1,
                    name="example",
                    tasks=[],
                ),
                WorkflowDefinitionRecord(
                    workflow_id=workflow_id,
                    revision=1,
                    name="example changed",
                    tasks=[],
                ),
            ]
        )

        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_unknown_workflow_status_is_rejected(self) -> None:
        definition = WorkflowDefinitionRecord(
            workflow_id=uuid4(), revision=1, name="example", tasks=[]
        )
        self.session.add(definition)
        self.session.flush()
        execution = WorkflowExecutionRecord(definition=definition, status="unknown")
        self.session.add(execution)

        with self.assertRaises(IntegrityError):
            self.session.flush()

    def test_negative_task_ordinal_is_rejected(self) -> None:
        definition = WorkflowDefinitionRecord(
            workflow_id=uuid4(), revision=1, name="example", tasks=[]
        )
        execution = WorkflowExecutionRecord(definition=definition, status="pending")
        execution.task_executions.append(
            TaskExecutionRecord(task_name="task", ordinal=-1, status="pending")
        )
        self.session.add(execution)

        with self.assertRaises(IntegrityError):
            self.session.flush()

    def test_execution_must_reference_an_existing_definition(self) -> None:
        self.session.add(
            WorkflowExecutionRecord(
                workflow_definition_id=uuid4(), status="pending"
            )
        )

        with self.assertRaises(IntegrityError):
            self.session.flush()


if __name__ == "__main__":
    unittest.main()
