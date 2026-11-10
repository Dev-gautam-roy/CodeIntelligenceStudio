from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.models.base import Base

# Ensure data directory exists
data_dir = settings.DATA_DIR
data_dir.mkdir(parents=True, exist_ok=True)

# Build reliable absolute database URL
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite"):
    db_path = (data_dir / "codeintel.db").resolve()
    db_url = f"sqlite:///{db_path.as_posix()}"
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initializes all database tables automatically for zero-configuration startup."""
    data_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that provides a transactional database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
