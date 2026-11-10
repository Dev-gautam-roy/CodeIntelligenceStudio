---
name: architecture-audit
description: Module dependency mapping, circular import detection, and architecture boundary verification.
when_to_use: Use when auditing codebase modularity, identifying technical debt, or mapping service/API interactions.
user-invocable: true
effort: high
allowed-tools:
  - run_command
  - read_file
---

# Architecture Audit Skill

## Purpose
Examine inter-module dependencies across a codebase, identify tightly coupled components, detect circular import cycles, and synthesize an architectural dependency graph.

## Execution Procedure
1. Parse AST imports for target codebase files.
2. Construct a directed graph $G = (V, E)$ where nodes are modules and edges represent import dependencies.
3. Apply Tarjan's or Kosaraju's algorithm to detect Strongly Connected Components (circular dependencies).
4. Discover REST, GraphQL, and RPC route definitions.
5. Generate an architecture report detailing module couplings, cyclomatic complexity hotspots, and recommendations.
