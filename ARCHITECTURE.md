# System Architecture — Code Intelligence Studio

## 1. Architectural Vision & Principles

Code Intelligence Studio is designed around five foundational tenets:

1. **Separation of Plane (Control vs Execution)**: The orchestrator and UI operate independently from the execution sandbox. Untrusted repository code never touches host system runtimes.
2. **Dual-Persistence Model**: Zero-configuration, file-backed local development (SQLite + ChromaDB local) with drop-in production scalability (PostgreSQL + distributed vector store).
3. **Graph-Driven Agentic Orchestration**: LangGraph coordinates stateful, dependency-aware multi-agent workflows with human-in-the-loop gates and durable checkpointing.
4. **Context-Folded Retrieval**: Token-conscious RAG pipeline with AST-aware chunking, caching, and multi-tier memory (short-term, episodic, semantic, project).
5. **Universal Interface**: Every operation is accessible via both a modern React Flow dashboard and a scriptable CLI (`codeintel`).

---

## 2. High-Level Component Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CLIENT LAYER                                    │
│   ┌───────────────────────────────────┐   ┌─────────────────────────────┐   │
│   │   Next.js 15 Web Dashboard        │   │   codeintel CLI (Typer)     │   │
│   │   (React Flow, Lucide, Tailwind)  │   │   (Rich Tables, JSON Output)│   │
│   └─────────────────┬─────────────────┘   └──────────────┬──────────────┘   │
└─────────────────────┼────────────────────────────────────┼──────────────────┘
                      │ HTTP / REST / SSE / WebSockets      │
                      ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             APPLICATION API LAYER                           │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │   FastAPI Gateway (Uvicorn, Python 3.13)                            │   │
│   │   • Auth & Policy Enforcement      • GitHub REST / GraphQL Client   │   │
│   │   • Workspace Sandboxing Manager   • Approval Gate Engine           │   │
│   │   • Event Stream / SSE Dispatcher  • Token Budget Tracker           │   │
│   └──────────────────────────────────┬──────────────────────────────────┘   │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │
                      ┌────────────────┴────────────────┐
                      ▼                                 ▼
┌──────────────────────────────────────────┐  ┌───────────────────────────────┐
│       LANGGRAPH AGENT ORCHESTRATION      │  │      RAG & MEMORY ENGINE      │
│  ┌────────────────────────────────────┐  │  │  ┌──────────────────────────┐ │
│  │ Supervisor Agent (Plan & Route)    │  │  │  │ AST Language Chunkers    │ │
│  ├────────────────────────────────────┤  │  │  ├──────────────────────────┤ │
│  │ Wave 1: Repo, Arch, Sec, Docs      │  │  │  │ ChromaDB Persistent Store│ │
│  ├────────────────────────────────────┤  │  │  ├──────────────────────────┤ │
│  │ Wave 2: Test & Sandbox Exec        │  │  │  │ Multi-Tier Memory Store  │ │
│  ├────────────────────────────────────┤  │  │  │ (Project, Episodic, RAG) │ │
│  │ Wave 3: Debug & Patch Gen          │  │  │  └──────────────────────────┘ │
│  ├────────────────────────────────────┤  │  └───────────────┬───────────────┘
│  │ Wave 4: Contribution & PR Gen      │  │                  │
│  └────────────────────────────────────┘  │                  │
└─────────────────────┬────────────────────┘                  │
                      │ Checkpoints                           │ Vectors
                      ▼                                       ▼
┌──────────────────────────────────────────┐  ┌───────────────────────────────┐
│          PERSISTENCE LAYER               │  │       ISOLATION SANDBOX       │
│  • SQLite (Local) / PostgreSQL (Prod)    │  │  • Docker Container Adapter   │
│  • Alembic Migrations                    │  │  • Windows Subprocess Sandbox │
│  • File Workspaces: workspaces/          │  │  • Path Boundary Enforcement  │
│  • Audit Logs & Checkpoints              │  │  • Resource Quotas & Timeouts │
└──────────────────────────────────────────┘  └───────────────────────────────┘
```

---

## 3. Subsystem Breakdown

### 3.1 Frontend Architecture (Next.js 15)
- **Framework**: Next.js App Router (React 19, TypeScript strict mode).
- **Styling**: Tailwind CSS + shadcn-inspired design primitives.
- **Visual Graphs**: `@xyflow/react` (React Flow) rendering:
  - Repository architecture graphs (modules, circular references, route connections).
  - Workflow dependency execution DAGs with live node states (`RUNNING`, `WAITING_FOR_APPROVAL`, `COMPLETED`).
- **State Management**: TanStack Query (v5) for asynchronous server caching and SSE event listeners; Zustand for local dashboard workspace state.

### 3.2 Backend Service Architecture (FastAPI)
- **Entrypoint**: `app/main.py` configuring CORS, rate-limiting, audit middleware, and routers under `/api/v1`.
- **Modular Domains**:
  - `api/v1/endpoints/`: Clean REST endpoints for Auth, GitHub, Repositories, Analysis, Agents, Workflows, Tasks, Approvals, Prompts, Memory, and Deployments.
  - `core/`: Application settings, security, logging, exceptions, and permissions.
  - `models/` & `schemas/`: SQLAlchemy declarative ORM models and Pydantic validation schemas.
  - `services/`: Encapsulated business logic decoupled from transport protocols.

### 3.3 Agent Orchestration (LangGraph)
- **State Machine Definition**: Defined in `app/orchestration/graph.py`.
- **Agent Registry**:
  1. `SupervisorAgent`: Dynamic task decomposition, budget enforcement, and wave synchronization.
  2. `RepositoryAgent`: File tree discovery, language detection, framework resolution.
  3. `ArchitectureAgent`: Import graph analysis, circular reference detection, service boundaries.
  4. `RagAgent`: AST-guided chunking, vector indexing, citation retrieval.
  5. `SecurityAgent`: Pattern-based and semantic secret discovery, prompt injection scanning.
  6. `TestingAgent`: Test discovery, test suite execution in sandbox, stdout/stderr parsing.
  7. `DebuggingAgent`: Stack trace diagnosis, AST-guided patch synthesis, regression testing.
  8. `DocumentationAgent`: Markdown report generation, API documentation, changelog synthesis.
  9. `ContributionAgent`: Branch staging, git diff validation, PR body generation.
  10. `DeploymentAgent`: Manifest validation, environment variable auditing, health check probing.
- **Task Lifecycle**:
  `PENDING` ➔ `QUEUED` ➔ `RUNNING` ➔ `WAITING_FOR_APPROVAL` (Gate) ➔ `COMPLETED` / `FAILED` / `RETRY_PENDING`.

### 3.4 RAG & Multi-Tier Memory Subsystem
- **Chunking Pipeline**:
  - Uses language-specific delimiters (classes, functions, decorators) for Python, JS/TS, Go, Rust, Java.
  - Maintains metadata: `file_path`, `start_line`, `end_line`, `symbol_name`, `commit_sha`.
- **Vector Storage**: ChromaDB with persistent collection storage at `data/chroma`.
- **Memory Tiers**:
  - *Short-Term Memory*: Conversation and immediate task context window.
  - *Project Memory*: Architectural facts, frameworks, repo configurations persisted in relational database.
  - *Semantic Memory*: Vector embeddings of code and docs.
  - *Episodic Memory*: Historical workflow execution logs, test run results, and resolution trajectories.

### 3.5 Security Boundaries & Sandboxing
- **Workspace Confinement**: Repositories are cloned strictly into `workspaces/:project_id/:commit_sha`. Any file read/write outside this root triggers a `PATH_TRAVERSAL_DETECTED` security block.
- **Sandbox Adapter Interface**:
  - `DockerSandbox`: Spawns isolated container with memory/CPU constraints, no host mount, and ephemeral filesystem.
  - `ProcessSandbox`: Fallback on Windows workstations with restricted command allowlists, timeout traps, and sandboxed working directories.
- **Secret Scanning**: Pre-flight regex and Shannon entropy scanners prevent secrets from entering vector memory or outbound PRs.
- **Prompt Injection Defense**: Untrusted content (READMEs, issues, commits) is filtered for instruction hijacking prior to agent ingestion.

---

## 4. Dual Persistence Architecture

| Domain | Local Development (Windows) | Production Environment (Cloud) |
| :--- | :--- | :--- |
| **Relational Data** | SQLite (`sqlite:///./data/codeintel.db`) | PostgreSQL 16+ via SQLAlchemy Async |
| **Vector Embeddings**| ChromaDB Persistent Client (`./data/chroma`) | Persistent Vector DB / Pgvector |
| **Workspaces** | Local Disk (`./workspaces`) | Cloud Object Storage / Ephemeral Volumes |
| **Task Queue** | ThreadPool + SQLite Task Engine | Celery / Redis / Background Workers |

Shared interfaces in `app/repositories/` ensure business logic has zero tight coupling to SQLite.

---

## 5. Deployment Topology

### Local Mode (Windows Developer Workstation)
- Next.js running on `http://localhost:3000`.
- FastAPI running on `http://127.0.0.1:8000`.
- Local SQLite database & ChromaDB store under `./data/`.
- Local Git commands executed with Windows Git credentials.

### Production Mode (Containerized Remote Architecture)
- Next.js compiled to standalone Node.js production server.
- FastAPI managed by Gunicorn/Uvicorn multi-worker behind Nginx reverse proxy.
- Managed PostgreSQL and Redis for distributed task state.
- Remote isolated execution workers (Kubernetes Jobs or isolated Docker daemons) for untrusted code execution.
