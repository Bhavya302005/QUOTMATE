from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class WorkOrderStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ─── Material Schemas ───────────────────────────────────────────────────────────

class MaterialBase(BaseModel):
    material_name: str = Field(..., min_length=1, max_length=200)
    quantity: Optional[Decimal] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=20)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    total_cost: Optional[Decimal] = Field(None, ge=0)

    @field_validator('quantity', 'unit_cost', 'total_cost', mode='before')
    @classmethod
    def _empty_decimal(cls, v):
        if v is None or v == '':
            return None
        return v


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    material_name: Optional[str] = Field(None, min_length=1, max_length=200)
    quantity: Optional[Decimal] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=20)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    total_cost: Optional[Decimal] = Field(None, ge=0)

    @field_validator('quantity', 'unit_cost', 'total_cost', mode='before')
    @classmethod
    def _empty_decimal(cls, v):
        if v is None or v == '':
            return None
        return v


class MaterialResponse(MaterialBase):
    id: str
    work_order_id: str
    order: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Work Order Schemas ─────────────────────────────────────────────────────────

class WorkOrderBase(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=200)
    client_phone: Optional[str] = Field(None, max_length=20)
    client_email: Optional[str] = Field(None, max_length=255)
    service_location: Optional[str] = None
    work_description: Optional[str] = None
    assigned_to: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    labor_hours: Optional[Decimal] = Field(None, ge=0)
    labor_rate: Optional[Decimal] = Field(None, ge=0)
    remarks: Optional[str] = None

    @field_validator('start_date', 'end_date', mode='before')
    @classmethod
    def _empty_dates(cls, v):
        if v is None or v == '':
            return None
        return v

    @field_validator('labor_hours', 'labor_rate', mode='before')
    @classmethod
    def _empty_labor_decimals(cls, v):
        if v is None or v == '':
            return None
        return v


class WorkOrderCreate(WorkOrderBase):
    linked_quotation_id: Optional[str] = None
    materials: Optional[List[MaterialCreate]] = Field(default_factory=list)

    @field_validator('linked_quotation_id', mode='before')
    @classmethod
    def _empty_linked_quotation(cls, v):
        if v is None or v == '':
            return None
        return v


class WorkOrderUpdate(BaseModel):
    client_name: Optional[str] = Field(None, min_length=1, max_length=200)
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    service_location: Optional[str] = None
    work_description: Optional[str] = None
    assigned_to: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    labor_hours: Optional[Decimal] = Field(None, ge=0)
    labor_rate: Optional[Decimal] = Field(None, ge=0)
    status: Optional[WorkOrderStatusEnum] = None
    remarks: Optional[str] = None
    linked_quotation_id: Optional[str] = None

    @field_validator('start_date', 'end_date', mode='before')
    @classmethod
    def _empty_dates(cls, v):
        if v is None or v == '':
            return None
        return v

    @field_validator('labor_hours', 'labor_rate', mode='before')
    @classmethod
    def _empty_labor_decimals(cls, v):
        if v is None or v == '':
            return None
        return v

    @field_validator('linked_quotation_id', mode='before')
    @classmethod
    def _empty_linked_quotation(cls, v):
        if v is None or v == '':
            return None
        return v


class WorkOrderResponse(WorkOrderBase):
    id: str
    document_id: str
    work_order_number: str
    status: WorkOrderStatusEnum
    linked_quotation_id: Optional[str] = None
    labor_cost: Optional[Decimal] = None
    material_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    before_photo_url: Optional[str] = None
    after_photo_url: Optional[str] = None
    customer_signature_url: Optional[str] = None
    materials: List[MaterialResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkOrderListItem(BaseModel):
    id: str
    document_id: str
    work_order_number: str
    client_name: str
    status: WorkOrderStatusEnum
    assigned_to: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_cost: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WorkOrderListResponse(BaseModel):
    items: List[WorkOrderListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class LaborCalculateRequest(BaseModel):
    labor_hours: Decimal = Field(..., ge=0)
    labor_rate: Decimal = Field(..., ge=0)
    materials: Optional[List[MaterialCreate]] = Field(default_factory=list)


class LaborCalculateResponse(BaseModel):
    labor_cost: Decimal
    material_cost: Decimal
    total_cost: Decimal


# ─── OCR → Work Order Schemas ───────────────────────────────────────────────────

class OCRToWorkOrderRequest(BaseModel):
    ocr_text: str = Field(..., min_length=1, description="Raw OCR text extracted from scanned document")
    document_id: Optional[str] = Field(None, description="Existing document ID to link (auto-created if omitted)")


class OCRMaterialSuggestion(BaseModel):
    material_name: str
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None


class OCRWorkOrderSuggestion(BaseModel):
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    service_location: Optional[str] = None
    work_description: Optional[str] = None
    assigned_to: Optional[str] = None
    remarks: Optional[str] = None
    materials: List[OCRMaterialSuggestion] = Field(default_factory=list)


class OCRToWorkOrderResponse(BaseModel):
    document_id: str
    suggested_work_order: Optional[OCRWorkOrderSuggestion] = None
    raw_text: str
    confidence_flags: List[str] = Field(default_factory=list)
    ai_confidence: Optional[str] = None
