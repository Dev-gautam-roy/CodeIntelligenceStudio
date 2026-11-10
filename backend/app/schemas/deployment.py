from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class DeploymentValidateRequest(BaseModel):
    repository_id: str
    target_environment: str = "production"  # staging, production


class DeploymentManifestAudit(BaseModel):
    file_path: str
    manifest_type: str  # Dockerfile, docker-compose, kubernetes
    is_valid: bool
    issues: List[str]
    missing_probes: List[str]


class DeploymentValidateResponse(BaseModel):
    is_deployable: bool
    audited_manifests: List[DeploymentManifestAudit]
    missing_environment_variables: List[str]
    exposed_secret_risks: List[str]
    recommendations: List[str]
