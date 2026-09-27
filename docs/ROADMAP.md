# Relay roadmap

Each version is deliberately scoped. Work listed as out of scope must wait for its named milestone or a documented roadmap change.

## v0.1 — Local Workflow Engine

- **Goal:** Execute a workflow DAG in one local Python process.
- **Features:** workflow and task definitions; DAG validation; dependency-aware execution; task status and result reporting; basic failure propagation; CLI or similarly minimal local entry point.
- **Concepts learned:** DAGs, topological ordering, execution state machines, task boundaries, deterministic testing.
- **Acceptance criteria:** a valid multi-step DAG runs in dependency order; invalid cycles and missing dependencies are rejected; a task failure produces an understandable execution outcome; automated tests cover normal and failure paths.
- **Out of scope:** persistence, databases, queues, retries, remote workers, APIs, scheduling, web UI, cloud deployment.

## v0.2 — Durable Execution

- **Goal:** Preserve workflow and task execution state so interrupted runs can be inspected and recovered locally.

- **Features:**
  - PostgreSQL persistence
  - SQLAlchemy persistence layer
  - Alembic migrations
  - persisted workflow definitions
  - WorkflowExecution records
  - TaskExecution records
  - durable task states and outputs appropriate to the design
  - restart/recovery behavior
  - execution history inspection

- **Concepts learned:** relational modeling, state persistence, transaction boundaries, schema evolution, recovery design, definition-vs-execution separation.

- **Acceptance criteria:**
  - an execution’s state survives process restart
  - interrupted work has a defined recoverable outcome
  - workflow definitions and executions are represented separately
  - schema changes are migration-driven
  - recovery scenarios are covered by automated tests

- **Out of scope:** Redis, distributed workers, automated retries, scheduling, GitHub integration, production cloud topology.

## v0.3 — Distributed Workers

- **Goal:** Move task execution from the coordinator process to independently running workers.

- **Features:**
  - Redis Streams as work transport
  - Redis consumer groups
  - independently started workers
  - worker identity
  - task dispatch
  - queue acknowledgements
  - pending-entry handling
  - basic abandoned-message recovery
  - separation of coordinator and worker responsibilities
  - concurrent execution of independent DAG branches

- **Concepts learned:** producer/consumer systems, Redis Streams, consumer groups, acknowledgements, pending entries, worker coordination, at-least-once delivery, backpressure basics.

- **Acceptance criteria:**
  - independently started workers execute dispatched tasks
  - multiple workers can process independent tasks concurrently
  - PostgreSQL remains authoritative for execution state
  - worker loss produces a defined visible outcome
  - integration tests exercise dispatch and worker failure

- **Out of scope:** durable retry policy, idempotency guarantees, DLQ behavior, scheduling, GitHub integration, comprehensive observability.

## v0.4 — Reliable Execution

- **Goal:** Make at-least-once distributed execution safe and recoverable enough for controlled use.
- **Features:** retry policies; idempotency keys or equivalent task safeguards; leases/acknowledgement handling as needed; failure recovery; dead-letter or terminal-failure handling appropriate to the design.
- **Concepts learned:** at-least-once delivery, duplicate execution, idempotency, retry backoff, poison work, failure modes.
- **Acceptance criteria:** transient failures retry according to policy; duplicate delivery does not corrupt intended outcomes for supported tasks; abandoned work becomes recoverable or terminally failed; reliability behavior is integration-tested.
- **Out of scope:** cron scheduling, third-party executor ecosystem, GitHub integration, complete tracing/metrics platform, cloud-native deployment.

## v0.5 — Portfolio MVP

**PORTFOLIO MVP**

- **Goal:** Turn Relay's execution engine into a coherent self-hosted developer product that can be demonstrated end-to-end.

- **Features:**

  Backend:
  - FastAPI
  - workflow creation/listing/inspection endpoints
  - execution start and inspection endpoints
  - execution cancellation where supported
  - SSE or equivalent live execution events
  - structured API errors

  Frontend:
  - React + TypeScript
  - workflow list
  - workflow detail
  - execution history
  - execution detail
  - task status visualization
  - retry/failure history
  - live execution updates

  Developer experience:
  - Docker Compose
  - one-command local startup
  - polished example workflows
  - end-to-end tests
  - CI pipeline
  - architecture documentation
  - local setup documentation

- **Concepts learned:** API design, frontend/backend boundaries, event streaming, integration testing, developer experience, system demonstration, architecture communication.

- **Acceptance criteria:**
  - a new developer can start Relay from the README
  - a workflow can be created and executed through the documented interface
  - independent DAG branches execute concurrently
  - failures and retries are visible
  - execution history survives restart
  - the UI receives live execution updates
  - the entire system starts through Docker Compose
  - automated tests exercise the end-to-end workflow path
  - CI runs the relevant test suites

- **Out of scope:** cron scheduling, general executor plugins, GitHub integration, advanced observability, production cloud deployment.

## v0.6 — Scheduling

- **Goal:** Start workflows on defined schedules.
- **Features:** interval and/or cron-like schedules; schedule persistence; missed-run policy; schedule enable/disable controls.
- **Concepts learned:** time semantics, clock drift, misfire handling, scheduler leadership, recurring idempotency.
- **Acceptance criteria:** schedules launch workflows predictably; restart behavior follows a documented missed-run policy; duplicate scheduled launches are prevented or safely handled; tests cover time-sensitive cases.
- **Out of scope:** third-party executors, GitHub triggers, full observability platform, cloud multi-region operation.

## v0.7 — Executor Ecosystem

- **Goal:** Support more than one deliberate way to execute task work.
- **Features:** executor contract; at least two supported executor implementations; executor selection; executor-focused documentation and tests.
- **Concepts learned:** stable interfaces, capability boundaries, plugin trade-offs, isolation models, compatibility.
- **Acceptance criteria:** the same supported workflow can run via two executors; executor failures are reported consistently; the contract is documented and tested.
- **Out of scope:** arbitrary untrusted plugins, marketplace/distribution system, GitHub integration, full cloud control plane.

## v0.8 — GitHub Integration

- **Goal:** Trigger and report Relay workflows from GitHub activity.
- **Features:** webhook ingestion; signature verification; event-to-workflow mapping; execution status reporting back to GitHub where applicable; replay-safe event handling.
- **Concepts learned:** webhooks, authentication, external event idempotency, API integration, security boundaries.
- **Acceptance criteria:** a verified supported GitHub event starts the intended workflow; duplicate delivery is safe; workflow outcome is visible to GitHub where configured; integration tests use representative payloads.
- **Out of scope:** integrations for every source-control provider, arbitrary automation marketplace, cloud multi-tenant service.

## v0.9 — Observability

- **Goal:** Make executions and system behavior diagnosable in operation.
- **Features:** structured logs; metrics; traces or correlated execution telemetry; health/readiness signals; dashboards or documented queries.
- **Concepts learned:** observability pillars, correlation IDs, service-level indicators, debugging distributed systems, alert design.
- **Acceptance criteria:** an operator can follow one execution across coordinator and worker activity; failures expose actionable context; core throughput, latency, and failure signals are available; observability paths are tested where practical.
- **Out of scope:** managed observability SaaS, guaranteed 24/7 operations, enterprise compliance program.

## v1.0 — Cloud Architecture

- **Goal:** Validate how Relay maps onto a production-oriented AWS-style architecture without requiring paid cloud infrastructure.

- **Features:**
  - Terraform
  - LocalStack-based infrastructure validation where practical
  - AWS reference architecture
  - mapping of local components to AWS managed services
  - PostgreSQL/RDS design
  - Redis/SQS trade-off analysis
  - worker/Lambda or container-worker comparison
  - artifact storage/S3 design
  - scaling plan
  - backup and recovery plan
  - security considerations
  - cost model
  - architecture decision records

- **Concepts learned:** Infrastructure as Code, cloud architecture, managed-service trade-offs, capacity planning, disaster recovery, cost awareness.

- **Acceptance criteria:**
  - infrastructure definitions are reproducible locally where supported
  - Relay's state, queue, worker and observability responsibilities map clearly to cloud services
  - common failure scenarios have documented recovery strategies
  - cost and architectural trade-offs are documented
  - no claim is made that Relay was deployed to production AWS unless it actually was

- **Out of scope:** paid production hosting, global active-active operation, enterprise compliance, unlimited scale.