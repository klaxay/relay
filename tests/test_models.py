import unittest

from relay import (
    TaskDefinition,
    TaskStatus,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStatus,
)


def uppercase(value: object | None) -> object:
    return str(value).upper()


class TaskDefinitionTests(unittest.TestCase):
    def test_construction_preserves_task_fields(self) -> None:
        task = TaskDefinition(
            name="format",
            work=uppercase,
            dependencies=["fetch"],
            input="relay",
        )

        self.assertEqual(task.name, "format")
        self.assertIs(task.work, uppercase)
        self.assertEqual(task.dependencies, ("fetch",))
        self.assertEqual(task.input, "relay")


class WorkflowDefinitionTests(unittest.TestCase):
    def test_construction_preserves_declaration_order(self) -> None:
        fetch = TaskDefinition("fetch", uppercase)
        format_task = TaskDefinition("format", uppercase, dependencies=["fetch"])
        publish = TaskDefinition("publish", uppercase, dependencies=["format"])

        workflow = WorkflowDefinition("release", [fetch, format_task, publish])

        self.assertEqual(
            tuple(task.name for task in workflow.tasks),
            ("fetch", "format", "publish"),
        )
        self.assertIsInstance(workflow.tasks, tuple)


class WorkflowExecutionTests(unittest.TestCase):
    def test_execution_initializes_pending_state_in_declaration_order(self) -> None:
        workflow = WorkflowDefinition(
            "release",
            [
                TaskDefinition("fetch", uppercase),
                TaskDefinition("format", uppercase, dependencies=["fetch"]),
            ],
        )

        execution = WorkflowExecution.create(workflow)

        self.assertIs(execution.workflow, workflow)
        self.assertEqual(execution.status, WorkflowStatus.PENDING)
        self.assertEqual(
            tuple(task_execution.task_name for task_execution in execution.task_executions),
            ("fetch", "format"),
        )
        self.assertTrue(
            all(
                task_execution.status is TaskStatus.PENDING
                and task_execution.result is None
                and task_execution.error is None
                for task_execution in execution.task_executions
            )
        )

    def test_repeated_executions_do_not_share_mutable_task_state(self) -> None:
        workflow = WorkflowDefinition("release", [TaskDefinition("fetch", uppercase)])

        first_execution = WorkflowExecution.create(workflow)
        second_execution = WorkflowExecution.create(workflow)
        first_task_execution = first_execution.task_executions[0]
        second_task_execution = second_execution.task_executions[0]

        first_task_execution.status = TaskStatus.SUCCEEDED
        first_task_execution.result = "RELAY"

        self.assertIsNot(first_execution.task_executions, second_execution.task_executions)
        self.assertIsNot(first_task_execution, second_task_execution)
        self.assertEqual(second_task_execution.status, TaskStatus.PENDING)
        self.assertIsNone(second_task_execution.result)


if __name__ == "__main__":
    unittest.main()
