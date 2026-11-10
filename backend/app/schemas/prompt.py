from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class PromptGenerateRequest(BaseModel):
    category: str  # repository_analysis, debugging, architecture, testing, refactoring, security, contribution, deployment
    target_context: Dict[str, Any]
    output_format: str = "markdown"  # "markdown" or "json"


class PromptGenerateResponse(BaseModel):
    category: str
    version: str
    prompt_text: str
    estimated_tokens: int
    recommended_tools: List[str]


class PromptVerifyRequest(BaseModel):
    prompt_text: str
    token_budget: Optional[int] = 4000


class PromptVerifyResponse(BaseModel):
    valid: bool
    score: float
    token_count: int
    missing_elements: List[str]
    contradictions: List[str]
    security_concerns: List[str]
    report: str


class InjectionScanRequest(BaseModel):
    text_content: str
    source_name: Optional[str] = "untrusted_file"


class InjectionScanResponse(BaseModel):
    is_safe: bool
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    detected_patterns: List[str]
    sanitized_text: str
