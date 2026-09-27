"""Validation and deterministic planning for Relay workflow definitions."""

from __future__ import annotations

from .models import TaskDefinition, WorkflowDefinition


class WorkflowValidationError(ValueError):
    """Raised when a workflow cannot be planned as a directed acyclic graph."""


def plan_workflow(workflow: WorkflowDefinition) -> tuple[str, ...]:
    """Validate *workflow* and return its task names in execution order.

    When more than one task is eligible, declaration order determines which
    task is planned first. The workflow definition is never mutated.
    """

    tasks_by_name = _index_tasks(workflow)
    _validate_dependencies(workflow, tasks_by_name)
    _validate_acyclic(workflow, tasks_by_name)

    planned: list[str] = []
    completed: set[str] = set()

    while len(planned) < len(workflow.tasks):
        for task in workflow.tasks:
            if task.name in completed:
                continue
            if all(dependency in completed for dependency in task.dependencies):
                planned.append(task.name)
                completed.add(task.name)
                break
        else:
            raise AssertionError("validated workflow could not be planned")

    return tuple(planned)


def _index_tasks(workflow: WorkflowDefinition) -> dict[str, TaskDefinition]:
    tasks_by_name: dict[str, TaskDefinition] = {}
    for task in workflow.tasks:
        if task.name in tasks_by_name:
            raise WorkflowValidationError(
                f"Workflow '{workflow.name}' has duplicate task name '{task.name}'."
            )
        tasks_by_name[task.name] = task
    return tasks_by_name


def _validate_dependencies(
    workflow: WorkflowDefinition, tasks_by_name: dict[str, TaskDefinition]
) -> None:
    for task in workflow.tasks:
        for dependency in task.dependencies:
            if dependency not in tasks_by_name:
                raise WorkflowValidationError(
                    f"Task '{task.name}' in workflow '{workflow.name}' depends on "
                    f"missing task '{dependency}'."
                )


def _validate_acyclic(
    workflow: WorkflowDefinition, tasks_by_name: dict[str, TaskDefinition]
) -> None:
    visited: set[str] = set()
    active: list[str] = []
    active_names: set[str] = set()

    def visit(task_name: str) -> None:
        if task_name in active_names:
            cycle_start = active.index(task_name)
            cycle = active[cycle_start:] + [task_name]
            raise WorkflowValidationError(
                f"Workflow '{workflow.name}' contains a dependency cycle: "
                f"{' -> '.join(cycle)}."
            )
        if task_name in visited:
            return

        active.append(task_name)
        active_names.add(task_name)
        for dependency in tasks_by_name[task_name].dependencies:
            visit(dependency)
        active.pop()
        active_names.remove(task_name)
        visited.add(task_name)

    for task in workflow.tasks:
        visit(task.name)
