# Installation & Setup Guide — Code Intelligence Studio

## Prerequisites
- **Operating System**: Windows 11 (64-bit) or modern Linux/macOS.
- **Python**: 3.11 to 3.13 (Python 3.13.2 verified).
- **Node.js**: 20 LTS or higher (Node v22.14.0 verified).
- **Git**: 2.40 or higher.
- **GitHub CLI (`gh`)**: Recommended for authenticated operations (`gh auth login`).

---

## Step-by-Step Installation

### 1. Clone the Project
```powershell
cd C:\Users\devga\OneDrive\Desktop
git clone https://github.com/Dev-gautam-roy/CodeIntelligenceStudio.git
cd CodeIntelligenceStudio
```

### 2. Verify Windows Environment
```powershell
.\scripts\verify-environment.ps1
```

### 3. Run Automated Setup
```powershell
.\scripts\setup.ps1
```
This script:
- Creates the Python virtual environment in `backend/.venv`.
- Installs all pinned backend packages (`fastapi`, `uvicorn`, `sqlalchemy`, `chromadb`, `typer`, `rich`, `pytest`).
- Installs frontend npm packages (`next`, `react`, `@xyflow/react`, `lucide-react`, `tailwindcss`).
- Initializes runtime storage folders (`data/`, `workspaces/`, `artifacts/`, `logs/`, `backups/`).

### 4. Start Platform Services
```powershell
.\scripts\start.ps1
```

### 5. Verify Telemetry & Health
```powershell
.\scripts\health-check.ps1
```
