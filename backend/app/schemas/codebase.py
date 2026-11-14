from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class FileTreeNode(BaseModel):
    name: str
    path: str
    type: str  # "file" or "directory"
    size: Optional[int] = None
    extension: Optional[str] = None
    children: Optional[List["FileTreeNode"]] = None


class FileContentResponse(BaseModel):
    path: str
    content: str
    language: str
    lines_count: int
    size_bytes: int


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class CodeReference(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    language: str
    snippet: str


class ChatResponse(BaseModel):
    reply: str
    references: List[CodeReference] = []
    model_used: str
