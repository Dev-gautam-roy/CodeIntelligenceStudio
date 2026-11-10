from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.core.logging import logger


class AgentContext(BaseModel):
    project_id: str
    repository_id: Optional[str] = None
    workspace_path: Optional[str] = None
    task_id: str
    token_budget: int = 4000
    parameters: Dict[str, Any] = {}


class AgentResult(BaseModel):
    agent_name: str
    status: str  # COMPLETED, FAILED, WAITING_FOR_APPROVAL
    summary: str
    evidence: Dict[str, Any] = {}
    tokens_used: int = 0
    duration_ms: int = 0
    requires_approval: bool = False
    approval_details: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    name: str = "BaseAgent"
    role: str = "General Engineering Agent"
    description: str = "Base agent specification."
    allowed_tools: List[str] = []
    prohibited_operations: List[str] = ["unrestricted_shell", "direct_git_push"]
    default_token_budget: int = 4000
    timeout_seconds: int = 60

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Executes the specialized task of this agent."""
        pass
