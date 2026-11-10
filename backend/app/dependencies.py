from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User


def get_current_user(db: Session = Depends(get_db)) -> User:
    """Returns the default developer user for local development, creating it if necessary."""
    user = db.query(User).filter(User.username == "dev-user").first()
    if not user:
        user = User(
            username="dev-user",
            email="developer@codeintel.local",
            role="admin",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
