from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin, generate_uuid


class Approval(Base, TimestampMixin):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)  # e.g., GIT_PUSH, GIT_FORK, CREATE_PR, EXECUTE_UNTRUSTED_CODE
    target_resource = Column(String(255), nullable=False)
    diff_payload = Column(Text, nullable=True)
    status = Column(String(30), default="PENDING", nullable=False, index=True)  # PENDING, APPROVED, REJECTED
    decided_by = Column(String(100), nullable=True)
    decided_at = Column(DateTime, nullable=True)

    task = relationship("Task", back_populates="approvals")
