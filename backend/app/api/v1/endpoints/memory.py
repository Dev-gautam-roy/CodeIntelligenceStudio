from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.memory import ProjectMemory
from app.schemas.memory import MemorySearchRequest, MemorySearchResponse, MemoryItem
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("/search", response_model=MemorySearchResponse)
def search_memory(request: MemorySearchRequest, db: Session = Depends(get_db)):
    # 1. Search semantic code chunks via ChromaDB
    code_results = RAGService.semantic_search(
        project_id=request.project_id,
        query=request.query,
        limit=request.limit,
    )

    items: List[MemoryItem] = []
    for c in code_results:
        items.append(
            MemoryItem(
                id=c["id"],
                memory_type="SEMANTIC_CODE",
                key=c["file_path"],
                content=c["content"],
                confidence=1.0,
                score=c.get("score"),
                source_citation=c.get("citation"),
            )
        )

    # 2. Query relational project memory
    proj_memories = (
        db.query(ProjectMemory)
        .filter(ProjectMemory.project_id == request.project_id)
        .limit(request.limit)
        .all()
    )
    for pm in proj_memories:
        items.append(
            MemoryItem(
                id=pm.id,
                memory_type=pm.memory_type,
                key=pm.key,
                content=pm.content,
                confidence=pm.confidence,
                score=1.0,
                source_citation=f"project_memory/{pm.key}",
            )
        )

    return MemorySearchResponse(
        query=request.query,
        results_count=len(items),
        items=items,
    )
