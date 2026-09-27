"""Run Relay's built-in v0.1 workflow demonstration."""

from relay import TaskDefinition, WorkflowDefinition, execute_workflow


def uppercase(value: object | None) -> object:
    return str(value).upper()


def add_exclamation(value: object | None) -> object:
    return f"{value}!"


def main() -> None:
    """Execute and print the deterministic local demonstration workflow."""
    workflow = WorkflowDefinition(
        "example",
        [
            TaskDefinition("format", uppercase, input="relay"),
            TaskDefinition(
                "publish", add_exclamation, dependencies=["format"], input="done"
            ),
        ],
    )

    execution = execute_workflow(workflow)
    print(f"Workflow {workflow.name}: {execution.status.value}")
    for task_execution in execution.task_executions:
        print(
            f"- {task_execution.task_name}: {task_execution.status.value} "
            f"result={task_execution.result!r} error={task_execution.error!r}"
        )


if __name__ == "__main__":
    main()
