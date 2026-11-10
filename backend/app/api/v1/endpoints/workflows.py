from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db, SessionLocal
from app.models.workflow import Workflow
from app.models.project import Project
from app.models.repository import Repository
from app.schemas.workflow import WorkflowCreateRequest, WorkflowResponse
from app.orchestration.graph import WorkflowOrchestrator

router = APIRouter()


async def execute_workflow_bg(workflow_id: str, project_id: str, workspace_path: str, repo_url: str):
    db: Session = SessionLocal()
    try:
        await WorkflowOrchestrator.run_full_pipeline(
            db=db,
            workflow_id=workflow_id,
            project_id=project_id,
            workspace_path=workspace_path,
            repository_url=repo_url,
        )
    finally:
        db.close()


@router.post("", response_model=WorkflowResponse)
def create_workflow(
    request: WorkflowCreateRequest,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo = db.query(Repository).filter(Repository.project_id == request.project_id).first()
    ws_path = repo.clone_path if repo else "."

    wf = Workflow(
        project_id=request.project_id,
        name=request.name,
        status="PENDING",
        plan_dag={
            "waves": ["Wave 1: Parallel Audit", "Wave 2: Testing", "Wave 3: Debugging", "Wave 4: Contribution & Approval"]
        },
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)

    # Launch background orchestration pipeline
    bg.add_task(execute_workflow_bg, wf.id, request.project_id, ws_path, request.repository_url)

    return WorkflowResponse.model_validate(wf)


@router.get("", response_model=List[WorkflowResponse])
def list_workflows(db: Session = Depends(get_db)):
    wfs = db.query(Workflow).order_by(Workflow.created_at.desc()).all()
    return [WorkflowResponse.model_validate(w) for w in wfs]


@router.get("/{id}", response_model=WorkflowResponse)
def get_workflow(id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    return WorkflowResponse.model_validate(wf)
