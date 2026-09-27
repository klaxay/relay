import unittest

from relay import TaskDefinition, WorkflowDefinition, WorkflowValidationError, plan_workflow


def identity(value: object | None) -> object | None:
    return value


class WorkflowPlanningTests(unittest.TestCase):
    def test_plans_dependencies_before_dependents_in_declaration_tie_order(self) -> None:
        workflow = WorkflowDefinition(
            "release",
            [
                TaskDefinition("publish", identity, dependencies=["package"]),
                TaskDefinition("lint", identity),
                TaskDefinition("package", identity, dependencies=["build"]),
                TaskDefinition("build", identity),
                TaskDefinition("notify", identity),
            ],
        )

        self.assertEqual(
            plan_workflow(workflow),
            ("lint", "build", "package", "publish", "notify"),
        )

    def test_plans_an_empty_workflow(self) -> None:
        workflow = WorkflowDefinition("empty", [])

        self.assertEqual(plan_workflow(workflow), ())

    def test_repeated_planning_is_deterministic_and_does_not_mutate_definition(self) -> None:
        workflow = WorkflowDefinition(
            "release",
            [
                TaskDefinition("build", identity),
                TaskDefinition("package", identity, dependencies=["build"]),
            ],
        )
        original_tasks = workflow.tasks
        original_dependencies = workflow.tasks[1].dependencies

        self.assertEqual(plan_workflow(workflow), ("build", "package"))
        self.assertEqual(plan_workflow(workflow), ("build", "package"))
        self.assertIs(workflow.tasks, original_tasks)
        self.assertIs(workflow.tasks[1].dependencies, original_dependencies)

    def test_rejects_a_missing_dependency(self) -> None:
        workflow = WorkflowDefinition(
            "release", [TaskDefinition("package", identity, dependencies=["build"])]
        )

        with self.assertRaisesRegex(
            WorkflowValidationError, "package.*missing task 'build'"
        ):
            plan_workflow(workflow)

    def test_rejects_a_self_dependency(self) -> None:
        workflow = WorkflowDefinition(
            "release", [TaskDefinition("build", identity, dependencies=["build"])]
        )

        with self.assertRaisesRegex(
            WorkflowValidationError, "build -> build"
        ):
            plan_workflow(workflow)

    def test_rejects_a_multi_task_cycle(self) -> None:
        workflow = WorkflowDefinition(
            "release",
            [
                TaskDefinition("build", identity, dependencies=["package"]),
                TaskDefinition("package", identity, dependencies=["build"]),
            ],
        )

        with self.assertRaisesRegex(
            WorkflowValidationError, "build -> package -> build"
        ):
            plan_workflow(workflow)

    def test_rejects_duplicate_task_names(self) -> None:
        workflow = WorkflowDefinition(
            "release",
            [TaskDefinition("build", identity), TaskDefinition("build", identity)],
        )

        with self.assertRaisesRegex(WorkflowValidationError, "duplicate task name 'build'"):
            plan_workflow(workflow)


if __name__ == "__main__":
    unittest.main()
