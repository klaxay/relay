# Relay

Relay is a learning-first, local workflow engine. In v0.1 it validates and
executes a task DAG synchronously in one Python process; execution state exists
only for that process.

## Run the included example

```bash
python main.py
```

The built-in workflow runs `format` before its dependent `publish` task and
prints the terminal workflow outcome plus one recorded result per task:

```text
Workflow example: succeeded
- format: succeeded result='RELAY' error=None
- publish: succeeded result='done!' error=None
```

The task lines are printed in workflow declaration order. Execution itself uses
the validated deterministic dependency order.

## Define a workflow

Build a `WorkflowDefinition` from ordered `TaskDefinition` values, then pass it
to `execute_workflow`:

```python
from relay import TaskDefinition, WorkflowDefinition, execute_workflow


workflow = WorkflowDefinition(
    "example",
    [
        TaskDefinition("format", lambda value: str(value).upper(), input="relay"),
        TaskDefinition(
            "publish",
            lambda value: f"{value}!",
            dependencies=["format"],
            input="done",
        ),
    ],
)

execution = execute_workflow(workflow)
```

Task callables receive only their configured `input`; dependency results are
not passed implicitly. Dependencies control when a task may run. If a task
raises an exception, it is recorded as `failed`, its dependents become
`blocked`, and unrelated branches continue. A workflow is `succeeded` only
when every task succeeds; otherwise it is `failed`.

## v0.1 limits

Relay v0.1 has no persistence, database, queue, retries, remote workers,
network API, scheduler, or workflow-file format. The built-in example is the
minimal runnable interface because arbitrary Python callables cannot be safely
represented in a general data file without adding configuration or plugin
machinery.

## v0.2 persistence schema

The v0.2 persistence layer uses PostgreSQL. Set `RELAY_DATABASE_URL` to a
SQLAlchemy PostgreSQL URL, then apply the schema with Alembic:

```bash
export RELAY_DATABASE_URL='postgresql+psycopg://user:password@localhost/relay'
uv run alembic upgrade head
```

This milestone provides the database records and schema only. Workflow
execution still uses the v0.1 in-memory path until persistence integration is
implemented.

## Tests

Run the automated tests:

```bash
python -m unittest discover -s tests -v
```
