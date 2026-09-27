# Relay contributor guide

Relay is a learning-first, self-hosted workflow execution engine for developers. The repository documentation is the source of truth for scope, decisions, and project state.

## Working agreement for Codex

- Before any substantial change, read `CURRENT.md`, `docs/PRODUCT.md`, `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, and the relevant section of `docs/LEARNING.md`.
- Treat the version in `CURRENT.md` as the active milestone. Implement only work explicitly in scope for that milestone; do not implement a later-version feature early, including as a hidden abstraction or configuration flag.
- Features may be implemented completely when they are in scope: include the user-facing behavior, error handling appropriate to the milestone, tests, and documentation. Do not leave deliberately incomplete production paths without recording them in `CURRENT.md`.
- Prefer the smallest clear design that satisfies the current milestone. Do not introduce frameworks, plugin systems, generalized interfaces, distributed components, or speculative abstractions before a present use requires them.
- Preserve existing user changes. Inspect the working tree before editing and avoid changing unrelated files.
- Add or update automated tests for behavior changes, and run the relevant test suite. Report what was run and any limitations.
- After a major change, provide a diff walkthrough: explain the important changed files, behavior, tests, and any trade-offs.
- At the completion of every milestone, update `CURRENT.md`, `docs/CHANGELOG.md`, and any affected product, roadmap, architecture, or learning documentation. Record architectural decisions in `docs/ARCHITECTURE.md` when they materially shape the system.
- Do not add dependencies, infrastructure, deployment configuration, or external services unless the active milestone requires them.

## Definition of done

A milestone item is done only when its acceptance criteria are met, tests pass, documentation reflects the delivered behavior, and the next work is accurately recorded in `CURRENT.md`.
