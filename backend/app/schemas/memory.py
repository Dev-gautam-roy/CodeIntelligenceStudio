from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class MemorySearchRequest(BaseModel):
    project_id: str
    query: str
    limit: int = 5
    memory_type: Optional[str] = None


class MemoryItem(BaseModel):
    id: str
    memory_type: str
    key: str
    content: str
    confidence: float
    score: Optional[float] = None
    source_citation: Optional[str] = None


class MemorySearchResponse(BaseModel):
    query: str
    results_count: int
    items: List[MemoryItem]
