# Test Strategy & Quality Assurance — Code Intelligence Studio

## 1. Quality Objectives
- **Zero Placeholder Code**: Every file contains production-grade, functional implementations.
- **Complete Test Coverage**: Unit tests, integration tests, and security tests covering all critical paths.
- **Fail-Safe Security**: Automated tests verifying that path traversal, prompt injection, and unauthorized Git writes are blocked.

---

## 2. Test Pyramid & Execution

### 2.1 Backend Tests (`backend/tests/`)
Executed via `pytest`:
- **Unit Tests (`tests/unit/`)**:
  - `test_security.py`: Tests Fernet credential encryption/decryption, regex and Shannon entropy secret detection, prompt injection vector discovery, and filesystem jail traversal enforcement.
  - `test_analysis.py`: Tests language line counts, framework detection across manifests, AST import extraction, and Tarjan's SCC circular dependency algorithm.
  - `test_rag.py`: Tests AST/syntax line-span boundary chunking and metadata preservation.
  - `test_agents.py`: Tests Agent Registry instantiation, agent contexts, and autonomous execution cycles.
- **Integration Tests (`tests/integration/`)**:
  - `test_api.py`: Tests live FastAPI endpoints (`/health`, `/api/v1/health`, prompt generation, prompt verification, and agent cataloging).

### 2.2 Frontend Verification (`frontend/`)
- **TypeScript Strict Compilation**: `npx tsc --noEmit` enforcing zero type errors across all React components, React Flow hooks, and API services.
- **Production Bundle Build**: `npm run build` validating clean Next.js static and server rendering.

### 2.3 CLI Verification (`cli/codeintel/`)
- `codeintel doctor` diagnostics table verification.
- `codeintel github validate <url>` live API check.
- `codeintel prompt injection-scan` security testing.

---

## 3. Continuous Execution
Run the complete automated test suite anytime with:
```powershell
.\scripts\test.ps1
```
