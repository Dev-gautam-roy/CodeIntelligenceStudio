from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin, generate_uuid


class AgentExecution(Base, TimestampMixin):
    __tablename__ = "agent_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    duration_ms = Column(Integer, default=0, nullable=False)
    status = Column(String(30), default="COMPLETED", nullable=False)
    tool_calls = Column(JSON, nullable=True)

    task = relationship("Task", back_populates="executions")
