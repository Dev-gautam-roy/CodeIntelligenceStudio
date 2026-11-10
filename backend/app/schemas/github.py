from typing import Optional, List
from pydantic import BaseModel, HttpUrl


class GitHubValidateRequest(BaseModel):
    url: str


class GitHubValidateResponse(BaseModel):
    valid: bool
    owner: str
    repo: str
    default_branch: str
    is_private: bool
    description: Optional[str] = None
    stars: int = 0
    forks_count: int = 0
    message: str


class GitHubForkRequest(BaseModel):
    url: str
    organization: Optional[str] = None


class GitHubForkResponse(BaseModel):
    forked: bool
    fork_url: str
    owner: str
    repo: str
    message: str
