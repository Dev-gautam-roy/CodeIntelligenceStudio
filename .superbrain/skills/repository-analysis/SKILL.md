---
name: repository-analysis
description: Autonomous multi-language repository scanning, stack detection, and structural analysis.
when_to_use: Use when ingesting a new repository or re-analyzing an existing codebase for technological composition and file trees.
user-invocable: true
effort: medium
allowed-tools:
  - run_command
  - read_file
---

# Repository Analysis Skill

## Purpose
Inspect an ingested repository workspace to identify technology stacks, languages, frameworks, package managers, entry points, and directory topology.

## Execution Procedure
1. Verify target repository directory in `./workspaces/{project_id}/{sha}`.
2. Scan root configuration files (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Dockerfile`).
3. Classify detected languages and package dependencies.
4. Locate primary application entrypoints (e.g. `main.py`, `index.ts`, `cmd/main.go`).
5. Output structured JSON and Markdown summary to `./artifacts/repository_analysis.json`.
