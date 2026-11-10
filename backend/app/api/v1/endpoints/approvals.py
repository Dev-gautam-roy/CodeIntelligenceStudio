from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.approval import Approval
from app.models.task import Task
from app.models.workflow import Workflow
from app.schemas.approval import ApprovalResponse, ApprovalDecisionRequest

router = APIRouter()


@router.get("", response_model=List[ApprovalResponse])
def list_approvals(status: str = None, db: Session = Depends(get_db)):
    query = db.query(Approval)
    if status:
        query = query.filter(Approval.status == status)
    approvals = query.order_by(Approval.created_at.desc()).all()
    return [ApprovalResponse.model_validate(a) for a in approvals]


@router.post("/{id}/approve", response_model=ApprovalResponse)
def approve_action(id: str, request: ApprovalDecisionRequest = None, db: Session = Depends(get_db)):
    approval = db.query(Approval).filter(Approval.id == id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval record not found.")

    approval.status = "APPROVED"
    approval.decided_by = "dev-user"
    approval.decided_at = datetime.now(timezone.utc)

    # Resume associated task and workflow
    task = db.query(Task).filter(Task.id == approval.task_id).first()
    if task:
        task.status = "COMPLETED"
        wf = db.query(Workflow).filter(Workflow.id == task.workflow_id).first()
        if wf:
            wf.status = "COMPLETED"

    db.commit()
    db.refresh(approval)
    return ApprovalResponse.model_validate(approval)


@router.post("/{id}/reject", response_model=ApprovalResponse)
def reject_action(id: str, request: ApprovalDecisionRequest = None, db: Session = Depends(get_db)):
    approval = db.query(Approval).filter(Approval.id == id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval record not found.")

    approval.status = "REJECTED"
    approval.decided_by = "dev-user"
    approval.decided_at = datetime.now(timezone.utc)

    task = db.query(Task).filter(Task.id == approval.task_id).first()
    if task:
        task.status = "CANCELLED"
        wf = db.query(Workflow).filter(Workflow.id == task.workflow_id).first()
        if wf:
            wf.status = "CANCELLED"

    db.commit()
    db.refresh(approval)
    return ApprovalResponse.model_validate(approval)
