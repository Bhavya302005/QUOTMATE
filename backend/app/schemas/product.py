from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


# Product Schemas
class ProductBase(BaseModel):
    """Base product schema"""
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    unit: str = Field(default="nos", max_length=20, description="Unit of measurement (nos, kg, ltr, etc.)")
    default_price: Optional[Decimal] = Field(None, ge=0, description="Default price per unit")
    gst_rate: Decimal = Field(default=18.00, ge=0, le=100, description="GST rate percentage")
    is_active: bool = Field(default=True, description="Whether product is active")


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    unit: Optional[str] = Field(None, max_length=20)
    default_price: Optional[Decimal] = Field(None, ge=0)
    gst_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for paginated product list"""
    products: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
