"""Domain models for local Relay workflow definitions and executions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence


TaskWork = Callable[[object | None], object]


class TaskStatus(str, Enum):
    """The lifecycle states available to one task in a workflow run."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"


class WorkflowStatus(str, Enum):
    """The lifecycle states available to one workflow run."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class TaskDefinition:
    """Reusable description of one unit of local work.

    The callable receives only this task's explicit input. Dependency outputs
    are not implicitly supplied.
    """

    name: str
    work: TaskWork
    dependencies: Sequence[str] = ()
    input: object | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "dependencies", tuple(self.dependencies))


@dataclass(frozen=True)
class WorkflowDefinition:
    """Reusable, ordered collection of task definitions.

    DAG correctness is intentionally not checked by this model. Validation is
    the separate responsibility of :func:`relay.plan_workflow`.
    """

    name: str
    tasks: Sequence[TaskDefinition]

    def __post_init__(self) -> None:
        object.__setattr__(self, "tasks", tuple(self.tasks))


@dataclass
class TaskExecution:
    """In-memory outcome state for one task in one workflow execution."""

    task_name: str
    status: TaskStatus = TaskStatus.PENDING
    result: object | None = None
    error: str | None = None


@dataclass
class WorkflowExecution:
    """In-memory outcome state for one run of a workflow definition."""

    workflow: WorkflowDefinition
    task_executions: tuple[TaskExecution, ...]
    status: WorkflowStatus = WorkflowStatus.PENDING

    @classmethod
    def create(cls, workflow: WorkflowDefinition) -> WorkflowExecution:
        """Create fresh task state in the workflow's declaration order."""

        return cls(
            workflow=workflow,
            task_executions=tuple(
                TaskExecution(task_name=task.name) for task in workflow.tasks
            ),
        )
