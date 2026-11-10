from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin, generate_uuid


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False, index=True)
    status = Column(String(30), default="PENDING", nullable=False, index=True)
    input_payload = Column(JSON, nullable=True)
    output_payload = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    token_usage = Column(Integer, default=0, nullable=False)
    execution_time_ms = Column(Integer, default=0, nullable=False)

    workflow = relationship("Workflow", back_populates="tasks")
    approvals = relationship("Approval", back_populates="task", cascade="all, delete-orphan")
    executions = relationship("AgentExecution", back_populates="task", cascade="all, delete-orphan")
