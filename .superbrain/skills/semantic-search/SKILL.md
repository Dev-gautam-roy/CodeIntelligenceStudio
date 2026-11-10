---
name: semantic-search
description: AST-guided semantic code retrieval, exact symbol lookup, and project memory querying.
when_to_use: Use when retrieving source context for an agent task, answering natural language queries about the codebase, or locating functions/classes.
user-invocable: true
effort: medium
allowed-tools:
  - run_command
  - read_file
---

# Semantic Search Skill

## Purpose
Query the persistent ChromaDB vector store and project memory to retrieve relevant, token-optimized code chunks with exact file path and line number citations.

## Execution Procedure
1. Verify ChromaDB collection state for the current `project_id`.
2. Compute dense embeddings for the natural language or code query.
3. Apply metadata filters (`project_id`, file extension, commit SHA).
4. Retrieve top-k semantic matches.
5. Format findings with explicit source citations: `path/to/file.py#L20-L45`.
