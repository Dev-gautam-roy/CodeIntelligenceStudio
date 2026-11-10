# Deployment Architecture & Production Guide — Code Intelligence Studio

## 1. Environments Overview

| Dimension | Local Workstation (Development) | Remote Cloud Server (Production) |
| :--- | :--- | :--- |
| **Host OS** | Windows 11 (64-bit) | Linux (Ubuntu 24.04 LTS / Alpine) |
| **Relational DB** | SQLite (`sqlite:///./data/codeintel.db`) | Managed PostgreSQL 16 (Async SQLAlchemy) |
| **Vector DB** | ChromaDB Persistent (`./data/chroma`) | Persistent Vector Database / Pgvector |
| **Sandbox** | Restricted Process Boundary | Hardened Docker / Kubernetes Ephemeral Pods |
| **Ingress** | Direct localhost:3000 / localhost:8000 | Nginx Reverse Proxy with TLS (Let's Encrypt) |

---

## 2. Remote Production Setup

### 2.1 Backend Deployment (FastAPI)
Run backend behind Gunicorn with Uvicorn worker class:
```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2.2 Frontend Deployment (Next.js)
Build standalone production bundle:
```bash
cd frontend
npm run build
npm run start -- -p 3000
```

### 2.3 Production Environment Variables (`.env`)
```ini
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql+asyncpg://codeintel_user:securepassword@db-host:5432/codeintel
SECRET_KEY=generate-secure-random-64-character-hex-string
SANDBOX_MODE=docker
BACKEND_CORS_ORIGINS=https://codeintel.yourdomain.com
```

### 2.4 Container Sandboxing Policy
In production, all untrusted repository test runs must execute via Docker containers with memory limits (`--memory=2048m`), CPU limits (`--cpus=2`), and network egress filtering.
