# Database Design & Persistence Specification — Code Intelligence Studio

## 1. Overview
Code Intelligence Studio utilizes a hybrid persistence architecture:
1. **Relational Database (SQLAlchemy + Alembic)**:
   - Local: SQLite (`sqlite:///./data/codeintel.db`)
   - Production: PostgreSQL 16 (`postgresql+asyncpg://user:pass@host:5432/codeintel`)
2. **Vector Database (ChromaDB)**:
   - Local: Persistent file storage (`./data/chroma`)
   - Production: Persistent Vector DB (ChromaDB remote server / Pgvector)
3. **Workspace Filesystem**:
   - Local: `./workspaces/{project_id}/{commit_sha}`
   - Ephemeral test patches and artifacts: `./artifacts/`

---

## 2. Relational Schema & Entities

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │    projects     │       │  repositories   │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK, UUID)   │◄──┐   │ id (PK, UUID)   │◄──┐   │ id (PK, UUID)   │
│ username (str)  │   └───┤ user_id (FK)    │   └───┤ project_id (FK) │
│ email (str)     │       │ name (str)      │       │ url (str)       │
│ role (str)      │       │ description     │       │ owner (str)     │
│ created_at      │       │ created_at      │       │ name (str)      │
└─────────────────┘       └────────┬────────┘       │ default_branch  │
                                   │                │ current_sha     │
                                   │                │ is_private      │
                                   │                │ created_at      │
                                   │                └─────────────────┘
                                   ▼
        ┌─────────────────────────────────────────────────────┐
        │                                                     │
        ▼                                                     ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│    workflows    │       │     tasks       │       │   approvals     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK, UUID)   │◄──┐   │ id (PK, UUID)   │◄──┐   │ id (PK, UUID)   │
│ project_id (FK) │   └───┤ workflow_id(FK) │   └───┤ task_id (FK)    │
│ name (str)      │       │ agent_name (str)│       │ action_type     │
│ status (enum)   │       │ status (enum)   │       │ target_resource │
│ trigger_type    │       │ input_data(JSON)│       │ diff_payload    │
│ created_at      │       │ output_data(JSON│       │ status (enum)   │
│ updated_at      │       │ retry_count     │       │ approved_by     │
└─────────────────┘       │ token_usage     │       │ decided_at      │
                          │ created_at      │       └─────────────────┘
                          └─────────────────┘
                                   │
                                   ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ agent_executions│       │ project_memories│       │   audit_logs    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK, UUID)   │       │ id (PK, UUID)   │       │ id (PK, UUID)   │
│ task_id (FK)    │       │ project_id (FK) │       │ event_type      │
│ agent_name      │       │ memory_type     │       │ user_id         │
│ prompt_tokens   │       │ key (str)       │       │ project_id      │
│ completion_toks │       │ content (text)  │       │ action          │
│ duration_ms     │       │ metadata (JSON) │       │ ip_address      │
│ status          │       │ created_at      │       │ created_at      │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

---

## 3. Entity Definitions & Field Details

### 3.1 `projects`
- `id` (VARCHAR(36), PK): UUID v4.
- `name` (VARCHAR(100), NOT NULL): Human-readable workspace name.
- `description` (TEXT): Project description and scope.
- `created_at` (TIMESTAMP): UTC creation timestamp.
- `updated_at` (TIMESTAMP): UTC update timestamp.

### 3.2 `repositories`
- `id` (VARCHAR(36), PK): UUID v4.
- `project_id` (VARCHAR(36), FK -> projects.id, NOT NULL).
- `url` (VARCHAR(255), NOT NULL): Canonical GitHub URL.
- `owner` (VARCHAR(100), NOT NULL): GitHub username or organization.
- `name` (VARCHAR(100), NOT NULL): GitHub repository name.
- `default_branch` (VARCHAR(50), DEFAULT 'main').
- `current_sha` (VARCHAR(40)): Head commit SHA analyzed.
- `is_private` (BOOLEAN, DEFAULT FALSE).
- `clone_path` (VARCHAR(255)): Relative workspace filesystem path.
- `indexed_at` (TIMESTAMP): Last completed vector index timestamp.

### 3.3 `workflows`
- `id` (VARCHAR(36), PK): UUID v4.
- `project_id` (VARCHAR(36), FK -> projects.id, NOT NULL).
- `name` (VARCHAR(100), NOT NULL): Workflow designation (e.g. `Full Audit & Test`).
- `status` (VARCHAR(30), DEFAULT 'PENDING'): Enum (`PENDING`, `RUNNING`, `WAITING_FOR_APPROVAL`, `COMPLETED`, `FAILED`, `CANCELLED`).
- `plan_dag` (JSON): Dependency graph of tasks.
- `created_at` (TIMESTAMP): UTC timestamp.

### 3.4 `tasks`
- `id` (VARCHAR(36), PK): UUID v4.
- `workflow_id` (VARCHAR(36), FK -> workflows.id, NOT NULL).
- `agent_name` (VARCHAR(50), NOT NULL): e.g., `ArchitectureAgent`, `TestingAgent`.
- `status` (VARCHAR(30), DEFAULT 'PENDING'): Enum (`PENDING`, `QUEUED`, `RUNNING`, `WAITING_FOR_APPROVAL`, `COMPLETED`, `FAILED`, `RETRY_PENDING`).
- `input_payload` (JSON): Typed parameters.
- `output_payload` (JSON): Structured output, evidence, and results.
- `error_message` (TEXT): Captured exception details (sanitized).
- `token_usage` (INTEGER, DEFAULT 0).
- `execution_time_ms` (INTEGER, DEFAULT 0).

### 3.5 `approvals`
- `id` (VARCHAR(36), PK): UUID v4.
- `task_id` (VARCHAR(36), FK -> tasks.id, NOT NULL).
- `action_type` (VARCHAR(50), NOT NULL): e.g. `GIT_FORK`, `GIT_PUSH`, `CREATE_PR`, `RUN_UNTRUSTED_TEST`.
- `target_resource` (VARCHAR(255), NOT NULL): e.g. `https://github.com/owner/repo/pulls`.
- `diff_payload` (TEXT): Full patch diff for user inspection.
- `status` (VARCHAR(30), DEFAULT 'PENDING'): Enum (`PENDING`, `APPROVED`, `REJECTED`).
- `created_at` (TIMESTAMP).
- `decided_at` (TIMESTAMP).

### 3.6 `project_memories`
- `id` (VARCHAR(36), PK): UUID v4.
- `project_id` (VARCHAR(36), FK -> projects.id, NOT NULL).
- `memory_type` (VARCHAR(30), NOT NULL): Enum (`PROJECT`, `EPISODIC`, `CONVENTION`).
- `key` (VARCHAR(100), NOT NULL): Identifier (e.g., `primary_framework`, `test_command`).
- `content` (TEXT, NOT NULL): Extracted memory text.
- `confidence` (FLOAT, DEFAULT 1.0).

---

## 4. ChromaDB Vector Store Schema

### Collection Name: `codeintel_chunks`
- **Embedding Model**: Default sentence-transformers or provider embedding (text-embedding-3-small compatible).
- **Document Content**: Sanitized source code chunk or markdown doc block.
- **Document Metadata**:
  ```json
  {
    "project_id": "string",
    "repository_id": "string",
    "file_path": "string (relative to workspace)",
    "language": "string",
    "symbol_name": "string (function/class name or null)",
    "start_line": 10,
    "end_line": 45,
    "commit_sha": "string (40 hex chars)",
    "chunk_hash": "string (sha256 of content)",
    "file_hash": "string (sha256 of file)"
  }
  ```

---

## 5. Migrations & Seed Strategy

- **Alembic**: Located in `backend/alembic/`.
- **Version Tracking**: `alembic_version` table in SQLite/PostgreSQL.
- Automatic table initialization on startup via `app.models.base.Base.metadata.create_all()` when running in local development mode for zero-touch onboarding.
