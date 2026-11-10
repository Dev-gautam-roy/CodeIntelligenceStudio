# User Guide — Code Intelligence Studio

## 1. Getting Started
Code Intelligence Studio provides two operational modes:
- **Graphical Dashboard**: High-density instrument control center accessible at `http://localhost:3000`.
- **Engineering CLI (`codeintel`)**: Console tool for terminal workflows and automated CI pipelines.

---

## 2. Ingesting & Analyzing a Repository
1. Open the Web Dashboard or terminal.
2. In the Repository Action Bar, paste a GitHub URL (e.g. `https://github.com/fastapi/fastapi`).
3. Select **Analyse** from the dropdown and click **Execute Repository Action**.
4. The platform will:
   - Validate repository availability via GitHub REST API.
   - Clone into an isolated workspace directory (`workspaces/:project_id/:commit_sha`).
   - Run AST analysis to map languages, frameworks, entry points, and routes.
   - Render the interactive dependency network in the **Architecture** tab.

---

## 3. Reviewing Architecture & Dependency Graphs
Navigate to the **Architecture** tab:
- **React Flow Graph**: Pan and zoom through detected modules and import connections.
- **Circular Dependencies**: Circular import cycles are identified and flagged to prevent architectural rot.
- **Framework Map**: Identified dependencies (e.g. FastAPI, Next.js, Django, Express) are cataloged with file references.

---

## 4. Triggering Multi-Agent Workflows
1. Select a repository action (e.g., **Test**, **Debug**, or **Prepare Contribution**).
2. The LangGraph supervisor orchestrates parallel execution waves:
   - **Wave 1**: Repository, Architecture, Security, and Documentation agents run concurrently.
   - **Wave 2**: Testing agent executes test suites in the isolated sandbox.
   - **Wave 3**: If tests fail, Debugging agent isolates stack traces and synthesizes a verified patch.
   - **Wave 4**: Contribution agent stages a feature branch and requests user sign-off.

---

## 5. Human-in-the-Loop Approvals Gate
Any action that writes to remote repositories or modifies upstream code requires explicit human approval:
- Clicking the amber **Approvals (N)** badge opens the review modal.
- Inspect the complete unified git diff.
- Choose **Approve & Publish** to proceed or **Reject** to abort.
