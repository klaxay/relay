# Relay product

## What Relay is

Relay is a self-hosted workflow execution engine for developers. It accepts a workflow definition made of dependent tasks, executes that work in dependency order, and progressively develops the durability, reliability, distribution, and operational visibility needed to study real workflow systems.

Relay is intentionally learning-first: each version is a usable increment and a focused opportunity to understand one layer of workflow-engine design.

## Target user

The primary user is a developer learning how workflow orchestration systems work by building and operating a small, understandable engine. A secondary user is a developer who wants to run simple, self-hosted developer workflows without adopting a large managed platform.

## Problems solved

- Express dependent work as a workflow rather than manually coordinating scripts.
- Execute tasks in a deterministic dependency order.
- Make execution progress, failures, retries, and recovery visible as the product matures.
- Separate a reusable workflow definition from each individual run.
- Provide a compact system in which queues, workers, persistence, APIs, and observability can be learned in context.

## Example use cases

- Run a local build → test → package workflow.
- Process an uploaded dataset through validation, transformation, and export steps.
- Coordinate a developer automation pipeline that later runs on independent workers.
- Trigger repository automation from GitHub events in the applicable milestone.
- Schedule recurring maintenance or reporting workflows in the applicable milestone.

## Core product concepts

- **Workflow definition:** a reusable DAG describing tasks and dependencies.
- **Task:** one named unit of work with an input, behavior, and outcome.
- **Workflow execution:** one specific run of a workflow definition.
- **Task execution:** the recorded attempt to run one task within a workflow execution.
- **DAG:** a directed acyclic graph; dependencies must not contain cycles.
- **Worker/executor:** a component that performs task work. These evolve from local execution to distributed worker and executor models.
- **Durability and recovery:** preserving enough state to resume or safely reason about interrupted work.

## Explicit non-goals

- Competing with full enterprise orchestrators or managed workflow platforms.
- A general-purpose business-process-management suite.
- Multi-tenant SaaS, billing, user administration, or a polished end-user UI before the roadmap calls for them.
- Exactly-once execution guarantees; the system will be designed around at-least-once delivery once queues exist.
- Premature support for arbitrary languages, plugins, cloud vendors, or unlimited scale.

## Product success criteria

Relay succeeds when it is possible to explain and demonstrate each roadmap stage with working code, tests, documentation, and operational evidence; a developer can define and execute workflows reliably at the current milestone’s scope; and the repository clearly records why the architecture evolved.
