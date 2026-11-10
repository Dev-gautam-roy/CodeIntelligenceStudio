---
name: github-contribution
description: Orchestrates git branch management, patch diff reviews, push operations, and pull request publication with mandatory approval gates.
when_to_use: Use when staging approved code fixes, submitting pull requests to upstream repositories, or creating forks.
user-invocable: true
effort: high
allowed-tools:
  - run_command
  - read_file
---

# GitHub Contribution Skill

## Purpose
Prepare, review, and submit open-source contributions or team pull requests to GitHub while enforcing strict human approval gates.

## Execution Procedure
1. Verify user identity and GitHub authentication token.
2. Ensure working changes are isolated on a dedicated feature branch.
3. Generate git diff and format unified patch preview.
4. Halt and trigger Human Approval Gate (`WAITING_FOR_APPROVAL`).
5. Upon explicit approval, push branch and call GitHub REST API to open a pull request.
