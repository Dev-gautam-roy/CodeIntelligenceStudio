---
name: prompt-engineering
description: Generates, verifies, and scans structured system and agent engineering prompts for safety, clarity, and budget compliance.
when_to_use: Use when designing agent instructions, checking prompts for contradictory constraints, or testing prompts against injection attacks.
user-invocable: true
effort: medium
allowed-tools:
  - run_command
  - read_file
---

# Prompt Engineering Skill

## Purpose
Author, inspect, optimize, and verify system and agent prompts to ensure deterministic outputs, token budget adherence, and injection resistance.

## Execution Procedure
1. Define clear role boundaries, allowed tools, and completion criteria.
2. Verify token budgets and context consumption.
3. Validate that input schemas and output response contracts are strictly typed.
4. Scan template for ambiguity, contradictory directives, and instruction leakage vulnerabilities.
5. Export verified prompts to Markdown and JSON formats.
