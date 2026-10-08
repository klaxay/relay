# Relay architecture

## v0.1 planned architecture

v0.1 is a deliberately small, single-process Python 3.11 application. A local entry point loads or constructs a workflow definition, validates its DAG, creates an in-memory workflow execution, and invokes eligible tasks in dependency order. Execution state and results live only for the lifetime of that process.

The planned components are:

- **Workflow definition model:** immutable-in-intent description of tasks and directed dependencies.
- **DAG validator and planner:** rejects missing dependencies and cycles, then determines eligible execution order.
- **Local executor:** invokes task work in the current process.
- **Execution state model:** records the status and outcome of the workflow and each task for the current run.
- **Minimal local interface:** starts an execution and reports its outcome.

There is no database, queue, remote worker, network API, scheduler, or infrastructure in v0.1.

The implemented domain model keeps definitions immutable-in-intent using frozen
dataclasses. A task has a name, local callable, explicit input, and dependency
names. A workflow preserves declaration order. Creating an execution creates
new mutable task-execution records in that same order; none of this state is
persisted. Task callables receive only their explicit input, never implicit
outputs from prerequisite tasks.

The DAG planner validates task names and dependency references before planning.
It rejects duplicate task names, missing dependencies, and cycles with a
`WorkflowValidationError`. A valid plan is a tuple of task names in topological
order. Where more than one task is eligible, declaration order is the
deterministic tie-breaker. Planning does not create execution state or invoke
task work.

The local executor plans before it creates an execution, then invokes tasks
synchronously in that plan order. It records task results and exceptions in
the existing task-execution records. A failed task blocks dependent tasks,
while independent branches still run; a workflow succeeds only when every task
succeeds. Execution state remains in memory for the process lifetime.

The v0.1 local interface is `python main.py`. It contains one built-in example
workflow and prints the workflow outcome followed by each task's recorded
status, result, and error in declaration order. This deliberately avoids a
workflow-file format: task definitions contain Python callables, and safely
loading arbitrary callables would require configuration or plugin machinery
outside v0.1's scope.

## Core architectural principles

- Keep the current milestone understandable end to end; favor explicit code over speculative layers.
- Workflow definitions and workflow executions are distinct. A definition is reusable intent; an execution is one time-bound run with its own state.
- Preserve execution state separately from work transport. When introduced, queues transport work but do not own authoritative execution state.
- PostgreSQL will eventually be the source of truth for workflow definitions, executions, task executions, and recovery-relevant state.
- Once queues are introduced, assume at-least-once delivery. Tasks and state transitions must tolerate duplicate delivery through idempotency and carefully designed ownership.
- Model failures explicitly. A terminal failure, retryable failure, and interrupted/unknown state should not be conflated.
- Make behavior testable at component boundaries before adding distribution.
- Add operational complexity only when a roadmap milestone makes it necessary.

## Future architecture (conceptual only)

Durable execution will introduce persistent state, eventually backed by PostgreSQL. Distributed execution will add a coordinator that plans eligible work, a queue that transports work, and workers that execute it. The coordinator and PostgreSQL—not the queue—will determine authoritative workflow and task execution state.

Reliable execution will build on at-least-once delivery with acknowledgement/lease design, retries, idempotency, and recovery handling. Later milestones may add scheduling, executor implementations, GitHub event ingestion, and correlated telemetry. Cloud architecture will package these responsibilities into deployable, secure, observable services without changing the core distinction between definition, execution state, and transport.

## v0.2 durable execution design

v0.2 keeps Relay single-process and local. PostgreSQL is the authoritative
store for workflow definitions and execution history. SQLAlchemy maps the
records, and Alembic owns schema changes.

Persist a workflow definition separately from each run. A definition stores
its stable identity, name, ordered task metadata (task names, dependencies,
and JSON-compatible configured inputs), and a revision number. It does not
store Python callables. Starting a run creates a `WorkflowExecution` with its
own identifier, a reference to the definition revision, start/finish times,
and workflow status. Its associated `TaskExecution` records store task name,
status, JSON-compatible result when available, error text, and start/finish
times. Keeping the definition revision referenced by a run preserves what was
declared for historical inspection when a definition is edited later.

Only JSON-compatible task inputs and results are durable in v0.2. Reject an
unsupported input before creating an execution; if a task returns a value that
cannot be encoded, record that task as failed with a clear serialization
error. Do not silently stringify arbitrary Python objects.

On startup, inspect nonterminal workflow executions. A task left `running` is
changed to `failed` with an interruption error because its work may have
produced external side effects and v0.2 cannot determine whether it is safe to
run again. Pending tasks in that execution become `blocked`; already terminal
task records remain unchanged. The workflow becomes `failed`. This policy
records uncertainty without retrying or claiming that work is safe to repeat.
Persist each outcome transition transactionally. A crash between task side
effects and recording its result remains an unknown outcome and is reported as
interrupted on restart.

Recovery applies only to nonterminal runs and is safe to repeat: once records
are terminal, later startups leave them unchanged. v0.2 does not resume tasks,
retry failures, guarantee exactly-once effects, or coordinate multiple Relay
processes.

## Architecture Decision Records

Record material decisions here using this lightweight format:

### ADR template

- **Title:**
- **Status:** Proposed | Accepted | Superseded
- **Context:**
- **Decision:**
- **Consequences:**

### ADR-001 — Begin with a single-process local engine

- **Status:** Accepted
- **Context:** Relay is learning-first and v0.1 is limited to local DAG execution.
- **Decision:** Use an in-memory, single-process architecture for v0.1.
- **Consequences:** The first version is easy to inspect and test, but has no durability or distributed execution; those concerns remain explicitly deferred.

### ADR-002 — Separate authoritative state from queue transport

- **Status:** Accepted
- **Context:** Future distributed workers require a transport mechanism but need a recoverable record of execution truth.
- **Decision:** PostgreSQL will eventually own authoritative execution state; queues will transport work only.
- **Consequences:** The design must tolerate at-least-once delivery and duplicate messages rather than relying on a queue as the workflow database.

### ADR-003 — Keep v0.1 task inputs explicit

- **Status:** Accepted
- **Context:** v0.1 needs reusable task definitions but does not yet define data flow between tasks.
- **Decision:** A task callable accepts only its explicitly configured input. Prerequisite results are not implicitly passed to task work.
- **Consequences:** The initial model stays clear and deterministic. Any future inter-task data-flow contract must be designed explicitly rather than becoming an accidental callable convention.

### ADR-004 — Persist definition revisions and inspect interrupted runs

- **Status:** Accepted
- **Context:** v0.2 needs durable local history and a restart outcome, while task work is arbitrary Python and may have external side effects.
- **Decision:** Store workflow metadata as versioned revisions separately from workflow and task execution records. Persist only JSON-compatible inputs and outputs; never persist callables. At startup, mark running tasks failed as interrupted, pending tasks blocked, and the workflow failed. Preserve terminal task records and never rerun work during recovery.
- **Consequences:** Historical runs remain tied to the definition revision they used. Recovery is deterministic and safe to repeat, but it reports uncertain work as failed and requires a future explicit retry/reliability design to execute it again.
