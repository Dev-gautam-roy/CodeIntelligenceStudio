from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin, generate_uuid


class Repository(Base, TimestampMixin):
    __tablename__ = "repositories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    url = Column(String(255), nullable=False)
    owner = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    default_branch = Column(String(100), default="main", nullable=False)
    current_sha = Column(String(40), nullable=True)
    is_private = Column(Boolean, default=False, nullable=False)
    clone_path = Column(String(255), nullable=True)
    indexed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="repositories")
