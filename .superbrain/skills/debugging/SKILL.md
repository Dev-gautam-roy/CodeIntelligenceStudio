---
name: debugging
description: Stack trace triage, AST root cause diagnosis, regression test creation, and patch synthesis.
when_to_use: Use when automated tests fail, runtime exceptions are reported, or reproduction scripts identify defects.
user-invocable: true
effort: high
allowed-tools:
  - run_command
  - read_file
  - edit_file
---

# Debugging Skill

## Purpose
Triage runtime errors and stack traces, isolate the offending source files, formulate a minimal defect hypothesis, and synthesize a verifiable patch.

## Execution Procedure
1. Parse error frames, file paths, line numbers, and exception messages.
2. Retrieve corresponding source lines and caller contexts.
3. Formulate root cause analysis.
4. Author candidate code patch on an isolated branch.
5. Re-run tests in the sandbox to verify defect resolution and prevent regressions.
