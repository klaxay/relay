# Current project state

**Current Version:** v0.2
**Status:** IN PROGRESS

## Current objective

Preserve workflow and task execution state so interrupted runs can be inspected and recovered locally.

## Completed milestones

- Milestone 1 — Define the local workflow domain model.
- Milestone 2 — Validate and deterministically plan workflow DAGs.
- Milestone 3 — Execute validated task plans locally and record outcomes.
- Milestone 4 — Provide a minimal runnable interface and finish v0.1
  documentation.

## v0.2 milestones

- Milestone 1 — Define durable records and restart behavior. COMPLETE.
- Milestone 2 — Build the PostgreSQL schema and persistence layer. COMPLETE.
- Milestone 3 — Integrate durable execution and history inspection.
- Milestone 4 — Implement and test restart recovery.
- Milestone 5 — Document v0.2 completion.

## Current work

Milestones 1 and 2 establish the durable record boundary and PostgreSQL-backed
schema in `docs/ARCHITECTURE.md`. SQLAlchemy records and the initial Alembic
migration are in place. Next is Milestone 3: integrate durable execution and
history inspection.

## Known issues

Workflow execution still uses the v0.1 in-memory path; the persistence layer is
not integrated until v0.2 milestone 3. Callable task behavior cannot be
reconstructed from persisted workflow metadata; recovery will inspect
interrupted runs and will not rerun work.
