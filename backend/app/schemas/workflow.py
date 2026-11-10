from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class WorkflowCreateRequest(BaseModel):
    project_id: str
    name: str
    repository_url: str
    requested_phases: Optional[List[str]] = None


class WorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    plan_dag: Optional[Dict[str, Any]] = None
