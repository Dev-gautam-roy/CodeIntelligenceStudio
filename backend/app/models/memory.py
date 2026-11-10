from sqlalchemy import Column, String, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin, generate_uuid


class ProjectMemory(Base, TimestampMixin):
    __tablename__ = "project_memories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    memory_type = Column(String(30), nullable=False)  # PROJECT, EPISODIC, CONVENTION
    key = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    metadata_payload = Column(JSON, nullable=True)

    project = relationship("Project", back_populates="memories")
