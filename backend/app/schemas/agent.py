from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class AgentInfo(BaseModel):
    name: str
    role: str
    description: str
    allowed_tools: List[str]
    token_budget: int
    timeout_seconds: int


class AgentRunRequest(BaseModel):
    agent_name: str
    project_id: str
    task_goal: str
    context: Optional[Dict[str, Any]] = None


class AgentRunResponse(BaseModel):
    task_id: str
    agent_name: str
    status: str
    result: Optional[Dict[str, Any]] = None
    token_usage: int
    execution_time_ms: int
