# Relay learning journal

Use each section during and after its milestone. Capture observations, trade-offs, failures, and revised mental models; do not treat the prompts as conclusions.

## v0.1 — Local Workflow Engine

Understand DAG representation, topological ordering, dependency readiness, task and workflow state transitions, and testing deterministic execution.

**Implementation learnings:**

- A frozen workflow definition and fresh mutable execution records make the
  definition-versus-run boundary visible without persistence.
- Tuple normalization preserves declaration order while preventing accidental
  mutation of a definition's task and dependency collections.
- Separating validation and planning from the definition model keeps a reusable
  workflow declaration lightweight while making invalid graphs fail before any
  task work is introduced.
- Declaration order provides a simple deterministic tie-breaker when multiple
  tasks are eligible, which makes DAG behavior straightforward to test.
- Planning before creating execution state ensures invalid definitions cannot
  leave behind a partial local run or invoke task work.
- Recording blocked dependents separately from failed tasks makes failure
  propagation visible while allowing independent branches to complete.
- A synchronous executor makes state transitions easy to observe before later
  milestones introduce persistence or concurrent workers.
- A built-in command-line demonstration is enough to make the local engine
  inspectable without prematurely designing a callable-loading configuration
  format.
- Subprocess testing the documented command verifies the user-facing boundary
  while focused unit tests cover model, planner, and executor behavior.

**Open questions:**

- How should validated dependency order and later task-result flow interact
  without obscuring task callable boundaries?

## v0.2 — Durable Execution

Understand durable state, persistence boundaries, recovery after interruption, schema evolution, and the difference between recorded state and in-memory process state.

**Implementation learnings:**

- Keep workflow definition revisions separate from run records so editing a
  workflow does not rewrite the meaning of historical executions.
- Store only JSON-compatible task inputs and results. Python callables are
  behavior supplied by the running program, not durable workflow data.
- Treat a task left running after process restart as uncertain: its external
  effects may have happened even though its result was not committed. Mark it
  interrupted/failed rather than automatically invoking it again.
- Recovery can be idempotent when it only transitions nonterminal records and
  leaves terminal task outcomes untouched.
- Mapping a definition revision to a row and referencing that row from each
  execution makes historical identity a database-enforced relationship.
- Database constraints protect the important invariants (unique revisions,
  valid statuses, and one task name per run) even when callers bypass domain
  validation.

**Open questions:**

- What registration convention will later let a local process reconnect
  persisted task metadata to callable behavior? v0.2 history and recovery do
  not require reloading arbitrary workflows for execution.
- Should future versions add a supported representation for non-JSON task
  artifacts, or keep large outputs outside the execution database?

## v0.3 — Distributed Workers

Understand coordinator/worker responsibilities, work queues, delivery semantics, backpressure, worker failure, and distributed-system failure boundaries.

**Implementation learnings:**

**Open questions:**

## v0.4 — Reliable Execution

Understand at-least-once delivery, retries and backoff, idempotency, acknowledgements or leases, duplicate work, and terminal failure handling.

**Implementation learnings:**

**Open questions:**

## v0.5 — Portfolio MVP

Understand how to turn engineering increments into a coherent product demonstration, explain trade-offs, and validate end-to-end developer experience.

**Implementation learnings:**

**Open questions:**

## v0.6 — Scheduling

Understand time zones, clock behavior, cron/interval semantics, missed runs, scheduler leadership, and recurring execution idempotency.

**Implementation learnings:**

**Open questions:**

## v0.7 — Executor Ecosystem

Understand interface design, executor capabilities, isolation trade-offs, compatibility, extension boundaries, and versioning.

**Implementation learnings:**

**Open questions:**

## v0.8 — GitHub Integration

Understand webhook verification, external API boundaries, event mapping, security, duplicate delivery, and integration testing.

**Implementation learnings:**

**Open questions:**

## v0.9 — Observability

Understand structured logging, metrics, tracing, correlation, service-level indicators, dashboards, and diagnosing distributed failures.

**Implementation learnings:**

**Open questions:**

## v1.0 — Cloud Architecture

Understand cloud service selection, network and identity boundaries, scaling, availability, backups, disaster recovery, cost, and operational trade-offs.

**Implementation learnings:**

**Open questions:**
