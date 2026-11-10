from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.agents.registry import AgentRegistry
from app.agents.base import AgentContext
from app.schemas.agent import AgentInfo, AgentRunRequest, AgentRunResponse

router = APIRouter()


@router.get("", response_model=List[AgentInfo])
def list_registered_agents():
    return AgentRegistry.list_agents()


@router.post("/run", response_model=AgentRunResponse)
async def run_single_agent(request: AgentRunRequest, db: Session = Depends(get_db)):
    try:
        agent = AgentRegistry.get_agent(request.agent_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    ctx = AgentContext(
        project_id=request.project_id,
        task_id=f"adhoc_{request.agent_name}",
        parameters=request.context or {},
    )

    result = await agent.execute(ctx)
    return AgentRunResponse(
        task_id=ctx.task_id,
        agent_name=result.agent_name,
        status=result.status,
        result=result.model_dump(),
        token_usage=result.tokens_used,
        execution_time_ms=result.duration_ms,
    )
