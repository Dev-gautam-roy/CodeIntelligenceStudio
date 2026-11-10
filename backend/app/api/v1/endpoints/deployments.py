from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.repository import Repository
from app.schemas.deployment import (
    DeploymentValidateRequest,
    DeploymentValidateResponse,
    DeploymentManifestAudit,
)

router = APIRouter()


@router.post("/validate", response_model=DeploymentValidateResponse)
def validate_deployment(request: DeploymentValidateRequest, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == request.repository_id).first()
    if not repo or not repo.clone_path:
        raise HTTPException(status_code=404, detail="Repository not found or not cloned.")

    ws_dir = Path(repo.clone_path)
    audited = []
    missing_vars = []
    secret_risks = []

    # Audit Dockerfile
    dockerfile = ws_dir / "Dockerfile"
    if dockerfile.exists():
        content = dockerfile.read_text(encoding="utf-8", errors="ignore")
        has_healthcheck = "HEALTHCHECK" in content
        is_root = "USER root" in content or "USER" not in content
        issues = []
        if is_root:
            issues.append("Container runs as default root user.")
        if not has_healthcheck:
            issues.append("Missing HEALTHCHECK instruction.")

        audited.append(
            DeploymentManifestAudit(
                file_path="Dockerfile",
                manifest_type="Dockerfile",
                is_valid=len(issues) == 0,
                issues=issues,
                missing_probes=["HEALTHCHECK"] if not has_healthcheck else [],
            )
        )

    # Check for committed .env files
    if (ws_dir / ".env").exists():
        secret_risks.append("Plaintext .env file detected in workspace.")

    is_deployable = len(secret_risks) == 0

    return DeploymentValidateResponse(
        is_deployable=is_deployable,
        audited_manifests=audited,
        missing_environment_variables=missing_vars,
        exposed_secret_risks=secret_risks,
        recommendations=[
            "Configure Docker HEALTHCHECK instruction.",
            "Use isolated non-root user in container execution.",
            "Store production credentials in secrets manager.",
        ],
    )
