from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    action_type: str
    target_resource: str
    diff_payload: Optional[str] = None
    status: str
    decided_by: Optional[str] = None
    decided_at: Optional[datetime] = None
    created_at: datetime


class ApprovalDecisionRequest(BaseModel):
    decision_reason: Optional[str] = None
