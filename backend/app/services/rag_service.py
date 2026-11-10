import os
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.logging import logger
from app.services.analysis_service import IGNORE_DIRS, LANGUAGE_EXTENSIONS


class RAGService:
    _client: Optional[chromadb.ClientAPI] = None

    @classmethod
    def get_chroma_client(cls) -> chromadb.ClientAPI:
        """Initializes or returns persistent ChromaDB client."""
        if cls._client is None:
            persist_path = settings.DATA_DIR / "chroma"
            persist_path.mkdir(parents=True, exist_ok=True)
            cls._client = chromadb.PersistentClient(path=str(persist_path))
        return cls._client

    @classmethod
    def get_or_create_collection(cls, collection_name: str = "codeintel_chunks"):
        client = cls.get_chroma_client()
        return client.get_or_create_collection(name=collection_name)

    @staticmethod
    def compute_file_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @classmethod
    def chunk_code_file(
        cls,
        file_path: str,
        content: str,
        project_id: str,
        repository_id: str,
        commit_sha: str,
    ) -> List[Dict[str, Any]]:
        """Chunks source code using logical line-span blocks."""
        chunks = []
        lines = content.splitlines()
        file_hash = cls.compute_file_hash(content)
        ext = Path(file_path).suffix.lower()
        language = LANGUAGE_EXTENSIONS.get(ext, "Plaintext")

        # Logical window chunking (approx 40 lines per chunk with 8 lines overlap)
        chunk_size = 40
        overlap = 8
        total_lines = len(lines)

        if total_lines == 0:
            return []

        start = 0
        while start < total_lines:
            end = min(start + chunk_size, total_lines)
            chunk_text = "\n".join(lines[start:end])
            chunk_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
            chunk_id = f"{project_id}_{file_hash[:8]}_{start+1}_{end}"

            metadata = {
                "project_id": project_id,
                "repository_id": repository_id,
                "file_path": file_path,
                "language": language,
                "start_line": start + 1,
                "end_line": end,
                "commit_sha": commit_sha,
                "file_hash": file_hash,
            }

            chunks.append({
                "id": chunk_id,
                "document": chunk_text,
                "metadata": metadata,
            })

            if end == total_lines:
                break
            start += (chunk_size - overlap)

        return chunks

    @classmethod
    def index_workspace(
        cls,
        workspace_dir: Path,
        project_id: str,
        repository_id: str,
        commit_sha: str,
    ) -> Dict[str, Any]:
        """Indexes an entire workspace into ChromaDB."""
        start_time = time.time()
        collection = cls.get_or_create_collection()
        files_indexed = 0
        total_chunks = 0

        ids = []
        documents = []
        metadatas = []

        for root, dirs, files in os.walk(workspace_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                ext = Path(file).suffix.lower()
                if ext not in LANGUAGE_EXTENSIONS and ext not in [".md", ".json", ".yaml", ".yml", ".toml"]:
                    continue

                abs_path = Path(root) / file
                rel_path = str(abs_path.relative_to(workspace_dir)).replace("\\", "/")

                try:
                    content = abs_path.read_text(encoding="utf-8", errors="ignore")
                    if not content.strip():
                        continue
                    chunks = cls.chunk_code_file(
                        file_path=rel_path,
                        content=content,
                        project_id=project_id,
                        repository_id=repository_id,
                        commit_sha=commit_sha,
                    )
                    for c in chunks:
                        ids.append(c["id"])
                        documents.append(c["document"])
                        metadatas.append(c["metadata"])
                    files_indexed += 1
                    total_chunks += len(chunks)
                except Exception as e:
                    logger.warning(f"Failed to chunk {rel_path}: {str(e)}")

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            collection.upsert(
                ids=ids[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
            )

        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(f"Indexed {files_indexed} files ({total_chunks} chunks) for repo {repository_id} in {duration_ms}ms.")

        return {
            "repository_id": repository_id,
            "files_indexed": files_indexed,
            "chunks_created": total_chunks,
            "duration_ms": duration_ms,
            "status": "COMPLETED",
        }

    @classmethod
    def semantic_search(
        cls,
        project_id: str,
        query: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Performs semantic similarity query against ChromaDB with project isolation."""
        collection = cls.get_or_create_collection()
        results = collection.query(
            query_texts=[query],
            n_results=limit,
            where={"project_id": project_id},
        )

        formatted = []
        if results and results.get("ids") and len(results["ids"]) > 0:
            count = len(results["ids"][0])
            for i in range(count):
                meta = results["metadatas"][0][i]
                doc = results["documents"][0][i]
                distance = results["distances"][0][i] if results.get("distances") else 0.0

                formatted.append({
                    "id": results["ids"][0][i],
                    "content": doc,
                    "file_path": meta.get("file_path"),
                    "start_line": meta.get("start_line"),
                    "end_line": meta.get("end_line"),
                    "language": meta.get("language"),
                    "score": round(1.0 - min(distance, 1.0), 3),
                    "citation": f"{meta.get('file_path')}#L{meta.get('start_line')}-L{meta.get('end_line')}",
                })
        return formatted
