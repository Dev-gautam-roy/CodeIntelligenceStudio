from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RepositoryCreateRequest(BaseModel):
    url: str
    project_id: Optional[str] = None
    branch: Optional[str] = None


class RepositoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    url: str
    owner: str
    name: str
    default_branch: str
    current_sha: Optional[str] = None
    is_private: bool
    clone_path: Optional[str] = None
    indexed_at: Optional[datetime] = None
    created_at: datetime


class RepositoryIndexResponse(BaseModel):
    repository_id: str
    files_indexed: int
    chunks_created: int
    duration_ms: int
    status: str
