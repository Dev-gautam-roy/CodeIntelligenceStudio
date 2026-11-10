from fastapi import APIRouter, HTTPException, Depends
from app.schemas.github import (
    GitHubValidateRequest,
    GitHubValidateResponse,
    GitHubForkRequest,
    GitHubForkResponse,
)
from app.services.github_service import GitHubService
from app.core.exceptions import CodeIntelError

router = APIRouter()


@router.post("/validate", response_model=GitHubValidateResponse)
async def validate_github_url(request: GitHubValidateRequest):
    try:
        data = await GitHubService.validate_repository(request.url)
        return GitHubValidateResponse(**data)
    except CodeIntelError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fork", response_model=GitHubForkResponse)
async def fork_github_repo(request: GitHubForkRequest):
    try:
        data = await GitHubService.fork_repository(request.url, request.organization)
        return GitHubForkResponse(**data)
    except CodeIntelError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
