from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(String(255))  # Increased for file paths and other long IDs
    old_value = Column(JSON)
    new_value = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(TIMESTAMP, server_default=func.now())
