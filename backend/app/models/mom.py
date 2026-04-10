from sqlalchemy import Column, String, Text, Date, Time, TIMESTAMP, ForeignKey, Boolean, Integer, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ActionItemPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionItemStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MOM(Base):
    """Minutes of Meeting model"""
    __tablename__ = "moms"
    
    id = Column(String(36), primary_key=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    meeting_title = Column(String(300), nullable=False)
    meeting_date = Column(Date, nullable=False)
    meeting_time = Column(Time)
    location = Column(String(300))
    attendees = Column(Text)  # JSON array of attendee names
    raw_notes = Column(Text, nullable=False)  # Original meeting notes
    ai_summary = Column(Text)  # AI-generated summary
    key_points = Column(Text)  # JSON array of key discussion points
    decisions = Column(Text)  # JSON array of decisions made
    next_steps = Column(Text)  # JSON array of next steps
    ai_confidence = Column(Integer)  # 0-100 confidence score for AI summary
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    document = relationship("Document", back_populates="mom")
    action_items = relationship("ActionItem", back_populates="mom", cascade="all, delete-orphan")


class ActionItem(Base):
    """Action items from meetings"""
    __tablename__ = "action_items"
    
    id = Column(String(36), primary_key=True)
    mom_id = Column(String(36), ForeignKey("moms.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    assigned_to = Column(String(200))
    due_date = Column(Date)
    priority = Column(Enum(ActionItemPriority), default=ActionItemPriority.MEDIUM)
    status = Column(Enum(ActionItemStatus), default=ActionItemStatus.PENDING)
    order = Column(Integer)  # Display order
    is_ai_generated = Column(Boolean, default=False)  # True if extracted by AI
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    mom = relationship("MOM", back_populates="action_items")
