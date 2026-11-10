from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.task import Task
from app.schemas.task import TaskResponse

router = APIRouter()


@router.get("", response_model=List[TaskResponse])
def list_tasks(workflow_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Task)
    if workflow_id:
        query = query.filter(Task.workflow_id == workflow_id)
    tasks = query.order_by(Task.created_at.asc()).all()
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/{id}", response_model=TaskResponse)
def get_task(id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return TaskResponse.model_validate(task)
