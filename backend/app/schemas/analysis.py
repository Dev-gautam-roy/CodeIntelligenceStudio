from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    repository_id: str
    target_path: Optional[str] = None


class ArchitectureAnalysisResponse(BaseModel):
    repository_id: str
    languages: Dict[str, int]
    frameworks: List[str]
    entry_points: List[str]
    modules_count: int
    circular_dependencies: List[List[str]]
    dependencies_graph: Dict[str, List[str]]
    api_routes: List[Dict[str, str]]
    summary: str


class SecurityFinding(BaseModel):
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    type: str  # SECRET_LEAK, PROMPT_INJECTION, INSECURE_DEPENDENCY
    file_path: str
    line_number: int
    description: str
    snippet: str
    recommendation: str


class SecurityAnalysisResponse(BaseModel):
    repository_id: str
    findings_count: int
    findings: List[SecurityFinding]
    scan_duration_ms: int
