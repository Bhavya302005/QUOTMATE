from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from typing import Optional, Dict, Any
import uuid
from datetime import datetime


def log_audit(
    db: Session,
    user_id: str,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    old_value: Optional[Dict[str, Any]] = None,
    new_value: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Create an audit log entry
    
    Args:
        db: Database session
        user_id: ID of the user performing the action
        action: Action being performed (e.g., 'login', 'register', 'update_profile')
        entity_type: Type of entity being affected (e.g., 'user', 'document')
        entity_id: ID of the entity being affected
        old_value: Previous value before the action (for updates)
        new_value: New value after the action (for updates)
        ip_address: IP address of the user
    
    Returns:
        Created AuditLog object
    """
    audit_log = AuditLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address
    )
    
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    
    return audit_log


def get_user_audit_logs(
    db: Session,
    user_id: str,
    limit: int = 50,
    offset: int = 0
):
    """
    Get audit logs for a specific user
    
    Args:
        db: Database session
        user_id: ID of the user
        limit: Maximum number of logs to return
        offset: Number of logs to skip
    
    Returns:
        List of AuditLog objects
    """
    return db.query(AuditLog).filter(
        AuditLog.user_id == user_id
    ).order_by(
        AuditLog.created_at.desc()
    ).limit(limit).offset(offset).all()


def get_entity_audit_logs(
    db: Session,
    entity_type: str,
    entity_id: str,
    limit: int = 50,
    offset: int = 0
):
    """
    Get audit logs for a specific entity
    
    Args:
        db: Database session
        entity_type: Type of entity (e.g., 'user', 'document')
        entity_id: ID of the entity
        limit: Maximum number of logs to return
        offset: Number of logs to skip
    
    Returns:
        List of AuditLog objects
    """
    return db.query(AuditLog).filter(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id
    ).order_by(
        AuditLog.created_at.desc()
    ).limit(limit).offset(offset).all()
