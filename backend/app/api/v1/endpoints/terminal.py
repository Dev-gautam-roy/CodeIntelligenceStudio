from pathlib import Path
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.repository import Repository
from app.services.sandbox_service import SandboxService
from app.core.exceptions import SecurityViolationError

router = APIRouter()


class TerminalCommandRequest(BaseModel):
    repository_id: str
    command: str


class TerminalCommandResponse(BaseModel):
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool


@router.post("/execute", response_model=TerminalCommandResponse)
def execute_terminal_command(request: TerminalCommandRequest, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == request.repository_id).first()
    if not repo or not repo.clone_path:
        raise HTTPException(status_code=404, detail="Repository not found or workspace not ready.")

    ws_dir = Path(repo.clone_path)
    try:
        res = SandboxService.execute_command(
            command=request.command,
            working_dir=ws_dir,
            timeout_seconds=30,
        )
        return TerminalCommandResponse(
            command=request.command,
            **res,
        )
    except SecurityViolationError as e:
        raise HTTPException(status_code=403, detail=e.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
