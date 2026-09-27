# Changelog

All notable changes to Relay will be documented in this file. The format is inspired by [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Project documentation and roadmap initialization.
- In-memory workflow and task definition models for v0.1.
- In-memory workflow and task execution-state models with independent state per run.
- Standard-library automated tests for domain-model construction and state isolation.
- DAG validation and deterministic topological planning for v0.1 workflows.
- Focused automated tests for valid DAG plans, missing dependencies, cycles,
  and duplicate task names.
- Synchronous local workflow execution with recorded task results, failures,
  blocked dependents, and terminal workflow outcomes.
- A documented minimal runnable local workflow example that prints deterministic
  workflow and task outcomes.
- A subprocess integration test for the documented `python main.py` command.

### Changed

- Nothing yet.

### Fixed

- Nothing yet.
