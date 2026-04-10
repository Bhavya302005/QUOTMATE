from sqlalchemy import Column, String, Text, DECIMAL, Date, Integer, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Quotation(Base):
    __tablename__ = "quotations"
    
    id = Column(String(36), primary_key=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_name = Column(String(200), nullable=False)
    customer_email = Column(String(255))
    customer_phone = Column(String(20))
    customer_address = Column(Text)
    customer_gst = Column(String(20))
    subtotal = Column(DECIMAL(12, 2), default=0)
    cgst_amount = Column(DECIMAL(12, 2), default=0)
    sgst_amount = Column(DECIMAL(12, 2), default=0)
    igst_amount = Column(DECIMAL(12, 2), default=0)
    discount_percent = Column(DECIMAL(5, 2), default=0)
    discount_amount = Column(DECIMAL(12, 2), default=0)
    is_gst_on = Column(Boolean, default=True)
    manual_total_amount = Column(DECIMAL(12, 2), nullable=True)
    grand_total = Column(DECIMAL(12, 2), default=0)
    valid_until = Column(Date)
    terms_conditions = Column(Text)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    document = relationship("Document", back_populates="quotation")
    items = relationship("QuotationItem", back_populates="quotation", cascade="all, delete-orphan")


class QuotationItem(Base):
    __tablename__ = "quotation_items"
    
    id = Column(String(36), primary_key=True)
    quotation_id = Column(String(36), ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"))
    item_order = Column(Integer)
    description = Column(String(500), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(20), default="nos")
    unit_price = Column(DECIMAL(12, 2), nullable=False)
    gst_rate = Column(DECIMAL(5, 2), default=18.00)
    gst_amount = Column(DECIMAL(12, 2))
    total = Column(DECIMAL(12, 2))
    is_free_text = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    quotation = relationship("Quotation", back_populates="items")
    product = relationship("Product", lazy="joined")
