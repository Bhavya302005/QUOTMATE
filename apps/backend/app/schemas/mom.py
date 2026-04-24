from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, time
from enum import Enum


# Enums
class ActionItemPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionItemStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Action Item Schemas
class ActionItemBase(BaseModel):
    """Base action item schema"""
    title: str = Field(..., min_length=1, max_length=500, description="Action item title")
    description: Optional[str] = Field(None, description="Detailed description")
    assigned_to: Optional[str] = Field(None, max_length=200, description="Person responsible")
    due_date: Optional[date] = Field(None, description="Due date")
    priority: ActionItemPriorityEnum = Field(default=ActionItemPriorityEnum.MEDIUM, description="Priority level")
    status: ActionItemStatusEnum = Field(default=ActionItemStatusEnum.PENDING, description="Current status")


class ActionItemCreate(ActionItemBase):
    """Schema for creating action item"""
    pass


class ActionItemUpdate(BaseModel):
    """Schema for updating action item"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[ActionItemPriorityEnum] = None
    status: Optional[ActionItemStatusEnum] = None


class ActionItemResponse(ActionItemBase):
    """Schema for action item response"""
    id: str
    mom_id: str
    order: Optional[int] = None
    is_ai_generated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# MOM Schemas
class MOMBase(BaseModel):
    """Base MOM schema"""
    meeting_title: str = Field(..., min_length=1, max_length=300, description="Meeting title")
    meeting_date: date = Field(..., description="Meeting date")
    meeting_time: Optional[time] = Field(None, description="Meeting time")
    location: Optional[str] = Field(None, max_length=300, description="Meeting location")
    attendees: Optional[List[str]] = Field(None, description="List of attendees")
    raw_notes: str = Field(..., min_length=1, description="Raw meeting notes")


class MOMCreate(MOMBase):
    """Schema for creating MOM"""
    document_id: Optional[str] = Field(None, description="Associated document ID (optional - will auto-create)")
    trigger_ai_summary: bool = Field(default=False, description="Run AI summarization while creating MOM")
    meeting_context: Optional[str] = Field(None, description="Optional context passed to AI summarization")
    original_image_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Source handwritten image URL from OCR upload"
    )
    ocr_raw_text: Optional[str] = Field(
        default=None,
        description="Raw OCR extracted text used as source notes"
    )
    ocr_confidence: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="OCR confidence score (0-100)"
    )


class MOMUpdate(BaseModel):
    """Schema for updating MOM"""
    meeting_title: Optional[str] = Field(None, min_length=1, max_length=300)
    meeting_date: Optional[date] = None
    meeting_time: Optional[time] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    raw_notes: Optional[str] = None
    ai_summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    decisions: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None


class MOMResponse(MOMBase):
    """Schema for MOM response"""
    id: str
    document_id: str
    ai_summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    decisions: Optional[List[str]] = None
    next_steps: Optional[List[str]] = None
    ai_confidence: Optional[int] = None
    action_items: List[ActionItemResponse] = []
    mom_number: Optional[str] = None  # From document
    status: Optional[str] = None  # From document
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MOMListResponse(BaseModel):
    """Schema for paginated MOM list"""
    items: List[MOMResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# AI Summarization Schemas
class SummarizeRequest(BaseModel):
    """Request to summarize meeting notes using AI"""
    raw_notes: str = Field(..., min_length=10, description="Raw meeting notes to summarize")
    meeting_context: Optional[str] = Field(None, description="Additional context about the meeting")


class SummarizeResponse(BaseModel):
    """AI summarization response"""
    summary: str = Field(..., description="AI-generated summary")
    key_points: List[str] = Field(default=[], description="Key discussion points")
    decisions: List[str] = Field(default=[], description="Decisions made")
    action_items: List[dict] = Field(default=[], description="Extracted action items")
    next_steps: List[str] = Field(default=[], description="Next steps")
    confidence: int = Field(..., ge=0, le=100, description="Confidence score")
    ai_model: str = Field(..., description="AI model used for summarization")
