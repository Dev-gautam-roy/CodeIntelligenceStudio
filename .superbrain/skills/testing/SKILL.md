---
name: testing
description: Discovers, configures, and executes repository test suites inside an isolated sandbox.
when_to_use: Use when validating repository baseline health, verifying defect reports, or validating candidate patches.
user-invocable: true
effort: high
allowed-tools:
  - run_command
  - read_file
---

# Testing Skill

## Purpose
Safely discover and execute unit, integration, and regression test suites inside the execution sandbox without exposing the host system.

## Execution Procedure
1. Identify test framework (e.g. `pytest`, `vitest`, `jest`, `go test`, `cargo test`).
2. Verify execution sandbox status (Docker container or restricted process boundary).
3. Execute tests with a strict timeout and resource cap.
4. Capture and parse structured results (`passed`, `failed`, `skipped`, durations).
5. Extract stack traces and failing assertions for downstream debugging.
