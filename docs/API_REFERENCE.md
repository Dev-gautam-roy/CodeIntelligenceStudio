# API Reference — Code Intelligence Studio

Base URL: `http://127.0.0.1:8000/api/v1`

---

## 1. System Health

### `GET /health` & `GET /api/v1/health`
Checks server responsiveness and database connection status.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "Code Intelligence Studio",
  "environment": "development",
  "database": "sqlite_connected",
  "version": "0.1.0"
}
```

---

## 2. GitHub Integration

### `POST /api/v1/github/validate`
Validates a GitHub repository URL, confirming accessibility and reading metadata via GitHub REST API.

**Request**:
```json
{
  "url": "https://github.com/fastapi/fastapi"
}
```

**Response `200 OK`**:
```json
{
  "valid": true,
  "owner": "fastapi",
  "repo": "fastapi",
  "default_branch": "master",
  "is_private": false,
  "description": "FastAPI framework, high performance, easy to learn...",
  "stars": 104602,
  "forks_count": 10207,
  "message": "Successfully verified repository fastapi/fastapi."
}
```

### `POST /api/v1/github/fork`
Triggers an authenticated GitHub fork via official GitHub API with token authorization.

---

## 3. Repositories

### `POST /api/v1/repositories/clone`
Clones a repository into an isolated workspace directory (`workspaces/:project_id/:commit_sha`) and registers the repository record.

### `GET /api/v1/repositories`
Lists all ingested repositories.

### `POST /api/v1/repositories/{id}/index`
AST-chunks all tracked code files and indexes them into the persistent ChromaDB collection.

---

## 4. Architecture & Security Analysis

### `POST /api/v1/analysis/architecture`
Executes AST import mapping and detects circular dependencies via Tarjan's SCC algorithm.

### `POST /api/v1/analysis/security`
Runs regex and Shannon entropy secret scanning and prompt injection detection.

---

## 5. Agents & Workflows

### `GET /api/v1/agents`
Lists all 10 specialized engineering agents, their roles, allowed tools, and token budgets.

### `POST /api/v1/workflows`
Launches a multi-wave autonomous LangGraph execution pipeline in the background.

### `GET /api/v1/workflows/{id}`
Retrieves workflow state and execution progress.

---

## 6. Approvals Gate

### `GET /api/v1/approvals`
Lists pending operations awaiting human sign-off (`GIT_PUSH`, `GIT_FORK`, `CREATE_PULL_REQUEST`).

### `POST /api/v1/approvals/{id}/approve`
Approves a staged action and resumes workflow execution.

### `POST /api/v1/approvals/{id}/reject`
Rejects a staged action and marks workflow as cancelled.

---

## 7. Prompts & Terminal

### `POST /api/v1/prompts/generate`
Generates structured system prompts for engineering roles.

### `POST /api/v1/prompts/injection-scan`
Scans untrusted content for prompt injection directives.

### `POST /api/v1/terminal/execute`
Executes sandboxed commands strictly inside the workspace boundary with allowlist enforcement.
