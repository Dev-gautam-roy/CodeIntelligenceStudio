# Code Intelligence Studio
### Autonomous AI Software Engineering & Repository Intelligence Platform

Code Intelligence Studio is an enterprise-grade autonomous AI software engineering platform. Given any accessible GitHub repository URL, it autonomously ingests, parses AST structures, models architectural relationships, detects defects and leaked secrets, sandboxes test runs, debugs failed assertions, generates validated code patches, and stages pull requests through strict human-in-the-loop approval gates.

---

## 1. System Requirements & Prerequisites

- **Host OS**: Windows 11 (64-bit) or modern Linux / macOS.
- **Runtimes**:
  - Python: `>= 3.11` (Python 3.13.2 verified)
  - Node.js: `>= 20.0.0` (Node.js v22.14.0 LTS verified)
  - npm: `>= 10.0.0`
  - Git: `>= 2.40.0` (Git for Windows 2.53.0 verified)
- **RAM**: Minimum 8 GB (16 GB recommended).
- **Disk**: 4 GB free on workspace drive.

---

## 2. Installation & Quick Start

1. **Verify Windows Environment**:
   ```powershell
   .\scripts\verify-environment.ps1
   ```

2. **Run Automated Setup**:
   ```powershell
   .\scripts\setup.ps1
   ```
   *Creates the Python virtual environment in `backend/.venv`, installs pinned backend dependencies, sets up the Next.js frontend packages, and initializes local data stores.*

3. **Launch Code Intelligence Studio**:
   ```powershell
   .\scripts\start.ps1
   ```
   *Access the platform:*
   - **Graphical Web Dashboard**: [http://localhost:3000](http://localhost:3000)
   - **FastAPI REST API**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Interactive OpenAPI Documentation**: [http://127.0.0.1:8000/api/v1/docs](http://127.0.0.1:8000/api/v1/docs)

4. **Stop Services Safely**:
   ```powershell
   .\scripts\stop.ps1
   ```
   *Cleanly terminates only application-owned backend and frontend processes without affecting unrelated tools.*

---

## 3. Configuration & Environment Variables

Copy `.env.example` to `.env` in the project root:

```bash
cp .env.example .env
```

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | Relational database connection string | `sqlite:///./data/codeintel.db` |
| `CHROMA_PERSIST_DIRECTORY` | Local vector database storage path | `./data/chroma` |
| `GITHUB_TOKEN` | GitHub PAT for authenticated private repos/forks | Optional (falls back to `gh` CLI) |
| `SANDBOX_MODE` | Execution sandbox adapter (`subprocess` or `docker`)| `subprocess` |
| `DEFAULT_TOKEN_BUDGET` | Max token budget per agent execution | `16000` |
| `MAX_AGENT_CONCURRENCY`| Parallel agent wave execution limit | `4` |

---

## 4. `codeintel` CLI Reference

The platform provides a scriptable console CLI built with Typer and Rich:

```powershell
# Diagnostics and Health
codeintel doctor
codeintel health

# GitHub Operations
codeintel github validate https://github.com/fastapi/fastapi
codeintel github fork https://github.com/fastapi/fastapi

# Repository Intelligence
codeintel repo clone https://github.com/fastapi/fastapi
codeintel repo analyze <REPOSITORY_ID>
codeintel repo index <REPOSITORY_ID>

# Security & Prompt Studio
codeintel security audit <REPOSITORY_ID>
codeintel prompt generate --category debugging
codeintel prompt verify "Role: System Analyst..."
codeintel prompt injection-scan "Ignore previous instructions..."

# Specialized Agents & Workflows
codeintel agent list
codeintel agent run RepositoryAgent <PROJECT_ID>
```

---

## 5. Security & Isolation Architecture

- **Defense-in-Depth**: Five security rings protect host machines from untrusted repositories.
- **Filesystem Jail**: Workspaces are confined strictly under `workspaces/:project_id/:commit_sha`. Path traversal attempts (`..`, `%00`) raise immediate security violations.
- **Sandboxed Execution**: Test suites and untrusted repository code run inside constrained Docker containers or strict process boundaries with command allowlists (`pytest`, `npm`, `git`, `python`, `cargo`, `go`).
- **Human Approval Gates**: Normal Mode requires explicit user confirmation prior to any git push, fork creation, or pull request publication.

---

## 6. Testing

Execute the automated test suite across units, integrations, security scanners, and AST parsers:

```powershell
.\scripts\test.ps1
```

Or run via pytest directly:
```powershell
cd backend
python -m pytest tests/ -v
```

---

## 7. Remote Production Deployment

For remote cloud deployments:
1. Switch `DATABASE_URL` to managed PostgreSQL (`postgresql+asyncpg://...`).
2. Run database migrations via Alembic.
3. Configure persistent remote vector store or Pgvector.
4. Set `SANDBOX_MODE=docker` to run all untrusted execution inside isolated container workers.
5. Deploy the Next.js frontend to standalone Node.js or edge container instances behind an HTTPS reverse proxy.
