from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


# Quotation Item Schemas
class QuotationItemBase(BaseModel):
    """Base quotation item schema"""
    description: str = Field(..., min_length=1, max_length=500, description="Item description")
    quantity: Decimal = Field(..., gt=0, description="Quantity")
    unit: str = Field(default="nos", max_length=20, description="Unit of measurement")
    unit_price: Decimal = Field(..., ge=0, description="Price per unit")
    gst_rate: Decimal = Field(default=18.00, ge=0, le=100, description="GST rate percentage")
    product_id: Optional[str] = Field(None, description="Reference to product if applicable")
    is_free_text: bool = Field(default=False, description="Whether item was manually entered")


class QuotationItemCreate(QuotationItemBase):
    """Schema for creating quotation item"""
    pass


class QuotationItemResponse(QuotationItemBase):
    """Schema for quotation item response"""
    id: str
    quotation_id: str
    item_order: Optional[int] = None
    gst_amount: Optional[Decimal] = None
    total: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Quotation Schemas
class QuotationBase(BaseModel):
    """Base quotation schema"""
    customer_name: str = Field(..., min_length=1, max_length=200, description="Customer name")
    customer_email: Optional[EmailStr] = Field(None, description="Customer email")
    customer_phone: Optional[str] = Field(None, max_length=20, description="Customer phone")
    customer_address: Optional[str] = Field(None, description="Customer address")
    customer_gst: Optional[str] = Field(None, max_length=20, description="Customer GST number")
    discount_percent: Decimal = Field(default=0, ge=0, le=100, description="Discount percentage")
    is_gst_on: bool = Field(default=True, description="Whether GST is applied to this quotation")
    manual_total_amount: Optional[Decimal] = Field(None, description="Manual total price override")
    valid_until: Optional[date] = Field(None, description="Quotation valid until date")
    terms_conditions: Optional[str] = Field(None, description="Terms and conditions")
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator('is_gst_on', mode='before')
    @classmethod
    def set_is_gst_on_default(cls, v):
        return True if v is None else v


class QuotationCreate(QuotationBase):
    """Schema for creating quotation"""
    document_id: Optional[str] = Field(None, description="Associated document ID (auto-created if not provided)")
    items: List[QuotationItemCreate] = Field(..., min_length=1, description="List of quotation items")
    is_igst: bool = Field(default=False, description="Whether to use IGST (inter-state) instead of CGST+SGST")


class QuotationUpdate(BaseModel):
    """Schema for updating quotation (all fields optional)"""
    customer_name: Optional[str] = Field(None, min_length=1, max_length=200)
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_address: Optional[str] = None
    customer_gst: Optional[str] = Field(None, max_length=20)
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    valid_until: Optional[date] = None
    terms_conditions: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[QuotationItemCreate]] = None
    is_igst: Optional[bool] = None
    is_gst_on: Optional[bool] = None
    manual_total_amount: Optional[Decimal] = None


class QuotationResponse(QuotationBase):
    """Schema for quotation response"""
    id: str
    document_id: str
    subtotal: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    discount_amount: Decimal
    grand_total: Decimal
    items: List[QuotationItemResponse] = []
    created_at: datetime
    updated_at: datetime
    # Fields from Document model
    quotation_number: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class QuotationListResponse(BaseModel):
    """Schema for paginated quotation list"""
    quotations: List[QuotationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# GST Calculation Schemas
class GSTCalculationRequest(BaseModel):
    """Request for GST calculation"""
    items: List[QuotationItemCreate] = Field(..., min_length=1)
    discount_percent: Decimal = Field(default=0, ge=0, le=100)
    is_igst: bool = Field(default=False, description="Use IGST instead of CGST+SGST")
    is_gst_on: bool = Field(default=True, description="Whether GST is applied")
    manual_total_amount: Optional[Decimal] = Field(None, description="Manual total price override")


class GSTCalculationResponse(BaseModel):
    """Response with calculated GST"""
    items: List[dict]
    subtotal: float
    discount_percent: float
    discount_amount: float
    taxable_amount: float
    cgst_rate: float
    cgst_amount: float
    sgst_rate: float
    sgst_amount: float
    igst_rate: float
    igst_amount: float
    total_gst: float
    grand_total: float
    is_igst: bool
    is_gst_on: bool
    manual_total_amount: Optional[float] = None


# OCR to Quotation Mapping
class OCRToQuotationRequest(BaseModel):
    """Request to map OCR text to quotation"""
    ocr_text: str = Field(..., min_length=1, description="OCR extracted text")
    document_id: Optional[str] = Field(None, description="Document ID for the quotation (optional, will auto-create if not provided)")


class OCRToQuotationResponse(BaseModel):
    """Response with mapped quotation fields"""
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None
    customer_gst: Optional[str] = None
    items: List[dict] = []
    confidence_flags: List[str] = Field(default=[], description="Fields that need review")
    raw_text: str
    document_id: Optional[str] = Field(None, description="Auto-created document ID")
    suggested_quotation: Optional[QuotationCreate] = None
    # Additional fields from AI parsing
    company_name: Optional[str] = Field(None, description="Quotation issuer company name")
    quotation_date: Optional[str] = Field(None, description="Date on the quotation")
    company_phone: Optional[str] = Field(None, description="Quotation issuer phone")
    company_email: Optional[str] = Field(None, description="Quotation issuer email")
    notes: Optional[str] = Field(None, description="General notes from quotation")
    ai_confidence: Optional[str] = Field(None, description="AI confidence: HIGH, MEDIUM, or LOW")
    ai_model: Optional[str] = Field(None, description="AI model used for parsing")
    lump_sum_total: Optional[float] = Field(None, description="Overall total written on quotation (when individual prices not given)")
    is_lump_sum_total: bool = Field(default=False, description="True when quotation has a lump-sum total instead of per-item prices")
