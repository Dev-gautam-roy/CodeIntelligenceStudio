import time
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.repository import Repository
from app.schemas.analysis import (
    AnalysisRequest,
    ArchitectureAnalysisResponse,
    SecurityAnalysisResponse,
)
from app.services.analysis_service import AnalysisService
from app.services.security_service import SecurityService

router = APIRouter()


@router.post("/architecture", response_model=ArchitectureAnalysisResponse)
def analyze_architecture(request: AnalysisRequest, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == request.repository_id).first()
    if not repo or not repo.clone_path:
        raise HTTPException(status_code=404, detail="Repository not found or not cloned.")

    ws_path = Path(repo.clone_path)
    if not ws_path.exists():
        raise HTTPException(status_code=404, detail="Workspace directory does not exist on disk.")

    arch_data = AnalysisService.analyze_architecture(ws_path)
    return ArchitectureAnalysisResponse(
        repository_id=repo.id,
        **arch_data,
    )


@router.post("/security", response_model=SecurityAnalysisResponse)
def scan_security(request: AnalysisRequest, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == request.repository_id).first()
    if not repo or not repo.clone_path:
        raise HTTPException(status_code=404, detail="Repository not found or not cloned.")

    start = time.time()
    ws_path = Path(repo.clone_path)
    all_findings = []

    # Check README for injection
    readme = ws_path / "README.md"
    if readme.exists():
        is_safe, risk, patterns, _ = SecurityService.scan_for_prompt_injection(readme.read_text(encoding="utf-8", errors="ignore"))
        if not is_safe:
            all_findings.append({
                "severity": risk,
                "type": "PROMPT_INJECTION",
                "file_path": "README.md",
                "line_number": 1,
                "description": f"Indirect prompt injection patterns detected: {patterns}",
                "snippet": "Prompt injection directive in repository file",
                "recommendation": "Sanitize untrusted README inputs before passing to LLM context.",
            })

    # Scan code for secrets and vulnerabilities across all supported languages
    code_extensions = {
        ".py", ".ts", ".js", ".jsx", ".tsx", ".dart", ".yaml", ".yml",
        ".json", ".env", ".html", ".sql", ".sh", ".java", ".kt", ".swift",
        ".go", ".rs", ".cpp", ".c", ".h"
    }
    ignore_dirs = {".git", "node_modules", ".venv", "__pycache__", ".dart_tool", "build", "dist"}

    for p in ws_path.glob("**/*"):
        if any(ignored in p.parts for ignored in ignore_dirs):
            continue
        if p.is_file() and p.suffix.lower() in code_extensions:
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                rel = str(p.relative_to(ws_path))
                findings = SecurityService.scan_content_for_secrets(rel, content)
                all_findings.extend([f.model_dump() for f in findings])
            except Exception:
                pass

    duration_ms = int((time.time() - start) * 1000)
    return SecurityAnalysisResponse(
        repository_id=repo.id,
        findings_count=len(all_findings),
        findings=all_findings,
        scan_duration_ms=duration_ms,
    )
