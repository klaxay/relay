import unittest

from relay import (
    TaskDefinition,
    TaskStatus,
    WorkflowDefinition,
    WorkflowStatus,
    WorkflowValidationError,
    execute_workflow,
)


class WorkflowExecutionTests(unittest.TestCase):
    def test_executes_tasks_in_planned_dependency_order_and_records_results(self) -> None:
        calls: list[str] = []

        def work(name: str):
            def run(value: object | None) -> object:
                calls.append(name)
                return value

            return run

        workflow = WorkflowDefinition(
            "release",
            [
                TaskDefinition("publish", work("publish"), dependencies=["package"], input=3),
                TaskDefinition("lint", work("lint"), input=1),
                TaskDefinition("package", work("package"), dependencies=["build"], input=2),
                TaskDefinition("build", work("build"), input=0),
            ],
        )

        execution = execute_workflow(workflow)

        self.assertEqual(calls, ["lint", "build", "package", "publish"])
        self.assertEqual(execution.status, WorkflowStatus.SUCCEEDED)
        self.assertEqual(
            [task_execution.status for task_execution in execution.task_executions],
            [
                TaskStatus.SUCCEEDED,
                TaskStatus.SUCCEEDED,
                TaskStatus.SUCCEEDED,
                TaskStatus.SUCCEEDED,
            ],
        )
        self.assertEqual(
            [task_execution.result for task_execution in execution.task_executions],
            [3, 1, 2, 0],
        )

    def test_empty_workflow_succeeds(self) -> None:
        execution = execute_workflow(WorkflowDefinition("empty", []))

        self.assertEqual(execution.status, WorkflowStatus.SUCCEEDED)
        self.assertEqual(execution.task_executions, ())

    def test_task_failure_records_error_and_blocks_dependent_tasks(self) -> None:
        dependent_called = False

        def fail(_: object | None) -> object:
            raise RuntimeError("build failed")

        def dependent(_: object | None) -> object:
            nonlocal dependent_called
            dependent_called = True
            return None

        workflow = WorkflowDefinition(
            "release",
            [
                TaskDefinition("build", fail),
                TaskDefinition("package", dependent, dependencies=["build"]),
            ],
        )

        execution = execute_workflow(workflow)
        build, package = execution.task_executions

        self.assertEqual(execution.status, WorkflowStatus.FAILED)
        self.assertEqual(build.status, TaskStatus.FAILED)
        self.assertEqual(build.error, "RuntimeError: build failed")
        self.assertEqual(package.status, TaskStatus.BLOCKED)
        self.assertEqual(
            package.error, "Blocked because dependencies did not succeed: build."
        )
        self.assertFalse(dependent_called)

    def test_independent_tasks_continue_after_a_failure(self) -> None:
        calls: list[str] = []

        def fail(_: object | None) -> object:
            calls.append("fail")
            raise ValueError("nope")

        def succeed(value: object | None) -> object:
            calls.append("succeed")
            return value

        workflow = WorkflowDefinition(
            "branches",
            [TaskDefinition("broken", fail), TaskDefinition("independent", succeed, input=4)],
        )

        execution = execute_workflow(workflow)

        self.assertEqual(calls, ["fail", "succeed"])
        self.assertEqual(execution.task_executions[1].status, TaskStatus.SUCCEEDED)
        self.assertEqual(execution.task_executions[1].result, 4)

    def test_invalid_workflow_fails_before_any_task_is_invoked(self) -> None:
        called = False

        def work(_: object | None) -> object:
            nonlocal called
            called = True
            return None

        workflow = WorkflowDefinition(
            "invalid", [TaskDefinition("package", work, dependencies=["missing"])]
        )

        with self.assertRaises(WorkflowValidationError):
            execute_workflow(workflow)

        self.assertFalse(called)

    def test_repeated_executions_keep_outcomes_isolated(self) -> None:
        workflow = WorkflowDefinition(
            "release", [TaskDefinition("build", lambda value: value, input="artifact")]
        )

        first_execution = execute_workflow(workflow)
        second_execution = execute_workflow(workflow)

        self.assertIsNot(first_execution.task_executions[0], second_execution.task_executions[0])
        self.assertEqual(first_execution.task_executions[0].result, "artifact")
        self.assertEqual(second_execution.task_executions[0].result, "artifact")


if __name__ == "__main__":
    unittest.main()
