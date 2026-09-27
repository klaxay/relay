"""Synchronous local execution for validated Relay workflows."""

from __future__ import annotations

from .models import TaskStatus, WorkflowDefinition, WorkflowExecution, WorkflowStatus
from .planning import plan_workflow


def execute_workflow(workflow: WorkflowDefinition) -> WorkflowExecution:
    """Run *workflow* locally and return its recorded in-memory outcome.

    The workflow is planned before execution state is created, so invalid
    definitions fail validation without invoking any task work. Tasks whose
    dependencies do not succeed are recorded as blocked; unrelated tasks
    continue in the deterministic planned order.
    """

    plan = plan_workflow(workflow)
    execution = WorkflowExecution.create(workflow)
    execution.status = WorkflowStatus.RUNNING

    tasks_by_name = {task.name: task for task in workflow.tasks}
    executions_by_name = {
        task_execution.task_name: task_execution
        for task_execution in execution.task_executions
    }

    for task_name in plan:
        task = tasks_by_name[task_name]
        task_execution = executions_by_name[task_name]
        blocked_dependencies = tuple(
            dependency
            for dependency in task.dependencies
            if executions_by_name[dependency].status is not TaskStatus.SUCCEEDED
        )
        if blocked_dependencies:
            task_execution.status = TaskStatus.BLOCKED
            task_execution.error = (
                "Blocked because dependencies did not succeed: "
                f"{', '.join(blocked_dependencies)}."
            )
            continue

        task_execution.status = TaskStatus.RUNNING
        try:
            task_execution.result = task.work(task.input)
        except Exception as error:
            task_execution.status = TaskStatus.FAILED
            task_execution.error = f"{type(error).__name__}: {error}"
        else:
            task_execution.status = TaskStatus.SUCCEEDED

    if all(
        task_execution.status is TaskStatus.SUCCEEDED
        for task_execution in execution.task_executions
    ):
        execution.status = WorkflowStatus.SUCCEEDED
    else:
        execution.status = WorkflowStatus.FAILED

    return execution
