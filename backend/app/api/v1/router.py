from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    github,
    repositories,
    analysis,
    agents,
    workflows,
    tasks,
    prompts,
    terminal,
    approvals,
    memory,
    deployments,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(github.router, prefix="/github", tags=["github"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["repositories"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(terminal.router, prefix="/terminal", tags=["terminal"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(deployments.router, prefix="/deployments", tags=["deployments"])
