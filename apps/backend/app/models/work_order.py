from sqlalchemy import Column, String, Text, Date, TIMESTAMP, ForeignKey, Enum, DECIMAL, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


class WorkOrderStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkOrder(Base):
    """Work Order model"""
    __tablename__ = "work_orders"

    id = Column(String(36), primary_key=True)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    linked_quotation_id = Column(String(36), ForeignKey("quotations.id", ondelete="SET NULL"), nullable=True, index=True)

    work_order_number = Column(String(50), unique=True, index=True)
    client_name = Column(String(200), nullable=False)
    client_phone = Column(String(20))
    client_email = Column(String(255))
    service_location = Column(Text)
    work_description = Column(Text)
    assigned_to = Column(String(100))

    start_date = Column(Date)
    end_date = Column(Date)

    labor_hours = Column(DECIMAL(6, 2))
    labor_rate = Column(DECIMAL(10, 2))
    labor_cost = Column(DECIMAL(12, 2))
    material_cost = Column(DECIMAL(12, 2))
    total_cost = Column(DECIMAL(12, 2))

    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.PENDING)

    before_photo_url = Column(String(500))
    after_photo_url = Column(String(500))
    customer_signature_url = Column(String(500))
    remarks = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    document = relationship("Document", back_populates="work_order")
    materials = relationship("WorkOrderMaterial", back_populates="work_order", cascade="all, delete-orphan")
    linked_quotation = relationship("Quotation", foreign_keys=[linked_quotation_id], lazy="joined")


class WorkOrderMaterial(Base):
    """Materials used in a work order"""
    __tablename__ = "work_order_materials"

    id = Column(String(36), primary_key=True)
    work_order_id = Column(String(36), ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    material_name = Column(String(200), nullable=False)
    quantity = Column(DECIMAL(10, 2))
    unit = Column(String(20))
    unit_cost = Column(DECIMAL(12, 2))
    total_cost = Column(DECIMAL(12, 2))
    order = Column(Integer)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    work_order = relationship("WorkOrder", back_populates="materials")
