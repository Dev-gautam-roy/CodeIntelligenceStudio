import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.repository import Repository
from app.schemas.codebase import (
    FileTreeNode,
    FileContentResponse,
    ChatRequest,
    ChatResponse,
    CodeReference,
)
from app.services.rag_service import RAGService
from app.services.analysis_service import LANGUAGE_EXTENSIONS, IGNORE_DIRS
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()

EXT_TO_LANG = {
    ".dart": "Dart",
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript React",
    ".js": "JavaScript",
    ".jsx": "JavaScript React",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".md": "Markdown",
    ".html": "HTML",
    ".css": "CSS",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".kts": "Kotlin Script",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".sql": "SQL",
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".toml": "TOML",
    ".xml": "XML",
}


def _build_tree(directory: Path, base_dir: Path) -> List[FileTreeNode]:
    """Recursively builds file tree omitting build, git, and virtual env folders."""
    nodes: List[FileTreeNode] = []
    try:
        entries = sorted(list(directory.iterdir()), key=lambda e: (not e.is_dir(), e.name.lower()))
    except Exception:
        return []

    for entry in entries:
        if entry.name in IGNORE_DIRS or entry.name.startswith("."):
            if entry.name != ".gitignore":
                continue

        rel_path = str(entry.relative_to(base_dir)).replace("\\", "/")
        if entry.is_dir():
            child_nodes = _build_tree(entry, base_dir)
            if child_nodes:  # Only show non-empty directories
                nodes.append(
                    FileTreeNode(
                        name=entry.name,
                        path=rel_path,
                        type="directory",
                        children=child_nodes,
                    )
                )
        else:
            ext = entry.suffix.lower()
            try:
                sz = entry.stat().st_size
            except Exception:
                sz = 0
            nodes.append(
                FileTreeNode(
                    name=entry.name,
                    path=rel_path,
                    type="file",
                    size=sz,
                    extension=ext,
                )
            )
    return nodes


@router.get("/{id}/file-tree", response_model=List[FileTreeNode])
def get_repository_file_tree(id: str, db: Session = Depends(get_db)):
    """Returns the complete directory and file structure of the cloned repository."""
    repo = db.query(Repository).filter(Repository.id == id).first()
    if not repo or not repo.clone_path:
        raise HTTPException(status_code=404, detail="Repository not found or not cloned.")

    ws_path = Path(repo.clone_path)
    if not ws_path.exists():
        raise HTTPException(status_code=404, detail="Repository workspace not found on disk.")

    tree = _build_tree(ws_path, ws_path)
    return tree


@router.get("/{id}/file-content", response_model=FileContentResponse)
def get_file_content(
    id: str,
    path: str = Query(..., description="Relative file path within repository"),
    db: Session = Depends(get_db),
):
    """Retrieves file source code content, line count, and language metadata."""
    repo = db.query(Repository).filter(Repository.id == id).first()
    if not repo or not repo.clone_path:
        raise HTTPException(status_code=404, detail="Repository not found or not cloned.")

    ws_path = Path(repo.clone_path).resolve()
    target_file = (ws_path / path).resolve()

    # Path traversal security check
    try:
        target_file.relative_to(ws_path)
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied: Path traversal detected.")

    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(status_code=404, detail=f"File '{path}' does not exist.")

    try:
        content = target_file.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read file: {str(e)}")

    lines = content.splitlines()
    ext = target_file.suffix.lower()
    language = EXT_TO_LANG.get(ext, "Plaintext")

    return FileContentResponse(
        path=path.replace("\\", "/"),
        content=content,
        language=language,
        lines_count=len(lines),
        size_bytes=len(content.encode("utf-8")),
    )


@router.post("/{id}/chat", response_model=ChatResponse)
async def chat_with_codebase(
    id: str,
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """Interactive RAG chat window allowing developers to converse with the codebase."""
    repo = db.query(Repository).filter(Repository.id == id).first()
    if not repo or not repo.clone_path:
        raise HTTPException(status_code=404, detail="Repository not found or not cloned.")

    ws_path = Path(repo.clone_path)
    user_query = request.message.strip()

    # Ensure collection exists and has been indexed
    try:
        raw_chunks = RAGService.semantic_search(
            project_id=repo.project_id,
            query=user_query,
            limit=5,
        )
    except Exception:
        raw_chunks = []

    # If Chroma collection was empty, auto-index workspace
    if not raw_chunks:
        try:
            RAGService.index_workspace(ws_path, repo.project_id, repo.id, repo.current_sha or "HEAD")
            raw_chunks = RAGService.semantic_search(
                project_id=repo.project_id,
                query=user_query,
                limit=5,
            )
        except Exception:
            raw_chunks = []

    # Format code references
    references: List[CodeReference] = []
    context_blocks = []

    for chunk in raw_chunks:
        file_path = chunk.get("file_path") or chunk.get("metadata", {}).get("file_path", "unknown")
        start_line = chunk.get("start_line") or chunk.get("metadata", {}).get("start_line", 1)
        end_line = chunk.get("end_line") or chunk.get("metadata", {}).get("end_line", 1)
        lang = chunk.get("language") or chunk.get("metadata", {}).get("language", "text")
        snippet = chunk.get("content") or chunk.get("document", "")

        references.append(
            CodeReference(
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                language=lang,
                snippet=snippet[:400],
            )
        )
        context_blocks.append(
            f"File: {file_path} (Lines {start_line}-{end_line}, Language: {lang})\n```\n{snippet}\n```"
        )

    # 1. Try Local Ollama if available
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("LOCAL_LLM_MODEL", "qwen2.5-coder:7b")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            context_text = "\n\n".join(context_blocks[:3])
            prompt = (
                f"You are Code Intelligence Studio, an AI repository expert. Answer the developer's question accurately using this codebase context:\n\n"
                f"{context_text}\n\n"
                f"Developer Question: {user_query}\n"
                f"Provide a clear, direct answer with exact code explanations, references, and suggestions."
            )
            resp = await client.post(
                f"{ollama_url}/api/generate",
                json={"model": ollama_model, "prompt": prompt, "stream": False},
            )
            if resp.status_code == 200:
                answer = resp.json().get("response", "")
                return ChatResponse(
                    reply=answer,
                    references=references,
                    model_used=f"Local Ollama ({ollama_model})",
                )
    except Exception:
        pass

    # 2. Local Deterministic Semantic RAG Synthesizer (Instant & Zero Cloud Cost)
    if references:
        top_ref = references[0]
        reply_lines = [
            f"### Analysis for: *\"{user_query}\"*",
            f"",
            f"Based on semantic indexing of **{repo.name}**, the most relevant implementation is located in **`{top_ref.file_path}`** (lines {top_ref.start_line}–{top_ref.end_line}).",
            f"",
            f"#### Code Excerpt from `{top_ref.file_path}`:",
            f"```{top_ref.language.lower()}",
            top_ref.snippet,
            f"```",
            f"",
            f"**Key Findings & Context:**",
            f"- **Target File**: `{top_ref.file_path}` ({top_ref.language})",
            f"- **Semantic Relevancy**: Matches concepts in your query regarding architecture, structure, and functions.",
        ]

        if len(references) > 1:
            reply_lines.append("")
            reply_lines.append(f"**Other Relevant Files Discovered:**")
            for ref in references[1:4]:
                reply_lines.append(f"- **`{ref.file_path}`** (lines {ref.start_line}–{ref.end_line})")

        reply_lines.append("")
        reply_lines.append("*Tip: You can click any file in the File Explorer tab to inspect its full source code.*")
        reply = "\n".join(reply_lines)
    else:
        # General repository metadata answer
        reply = (
            f"### Repository Information: **{repo.owner}/{repo.name}**\n\n"
            f"- **Default Branch**: `{repo.default_branch}`\n"
            f"- **Clone Location**: `{repo.clone_path}`\n\n"
            f"I searched the indexed semantic vector store for *\"{user_query}\"*, but no specific code chunks exceeded the similarity threshold. "
            f"You can browse all files directly in the **Code Explorer** tab on the left."
        )

    return ChatResponse(
        reply=reply,
        references=references,
        model_used="Local ChromaDB RAG Engine (all-MiniLM-L6-v2)",
    )
