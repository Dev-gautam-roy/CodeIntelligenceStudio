from sqlalchemy import Column, String, Text, JSON
from app.models.base import Base, TimestampMixin, generate_uuid


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    project_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(255), nullable=True)
    status = Column(String(30), nullable=False)
    ip_address = Column(String(45), nullable=True)
    details = Column(JSON, nullable=True)
