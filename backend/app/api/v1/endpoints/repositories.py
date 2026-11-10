from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.repository import Repository
from app.models.project import Project
from app.schemas.repository import (
    RepositoryCreateRequest,
    RepositoryResponse,
    RepositoryIndexResponse,
)
from app.services.github_service import GitHubService
from app.services.workspace_service import WorkspaceService
from app.services.rag_service import RAGService
from app.core.exceptions import CodeIntelError

router = APIRouter()


@router.post("/clone", response_model=RepositoryResponse)
async def clone_repository(request: RepositoryCreateRequest, db: Session = Depends(get_db)):
    # 1. Validate GitHub URL
    val_data = await GitHubService.validate_repository(request.url)

    # 2. Assign or create Project
    project_id = request.project_id
    if not project_id:
        proj = Project(name=f"{val_data['owner']}/{val_data['repo']}")
        db.add(proj)
        db.commit()
        db.refresh(proj)
        project_id = proj.id

    # 3. Perform Git Clone into isolated workspace
    try:
        dest_dir, head_sha = WorkspaceService.clone_repository(
            repo_url=request.url,
            project_id=project_id,
            branch=request.branch or val_data.get("default_branch"),
        )
    except CodeIntelError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())

    # 4. Save Repository in DB
    repo = Repository(
        project_id=project_id,
        url=request.url,
        owner=val_data["owner"],
        name=val_data["repo"],
        default_branch=val_data["default_branch"],
        current_sha=head_sha,
        is_private=val_data["is_private"],
        clone_path=str(dest_dir),
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)

    return RepositoryResponse.model_validate(repo)


@router.get("", response_model=List[RepositoryResponse])
def list_repositories(db: Session = Depends(get_db)):
    repos = db.query(Repository).order_by(Repository.created_at.desc()).all()
    return [RepositoryResponse.model_validate(r) for r in repos]


@router.get("/{id}", response_model=RepositoryResponse)
def get_repository(id: str, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    return RepositoryResponse.model_validate(repo)


@router.post("/{id}/index", response_model=RepositoryIndexResponse)
def index_repository(id: str, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == id).first()
    if not repo or not repo.clone_path:
        raise HTTPException(status_code=404, detail="Repository not found or not cloned.")

    ws_dir = Path(repo.clone_path)
    res = RAGService.index_workspace(
        workspace_dir=ws_dir,
        project_id=repo.project_id,
        repository_id=repo.id,
        commit_sha=repo.current_sha or "HEAD",
    )
    return RepositoryIndexResponse(**res)
