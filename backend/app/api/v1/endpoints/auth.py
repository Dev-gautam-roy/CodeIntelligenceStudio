from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        user = User(
            username=request.username,
            email=f"{request.username}@codeintel.local",
            role="developer",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return TokenResponse(
        access_token=f"codeintel-local-token-{user.id}",
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
def logout():
    return {"message": "Successfully logged out."}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
