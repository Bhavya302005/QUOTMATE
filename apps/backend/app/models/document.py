from sqlalchemy import Column, String, Enum, DECIMAL, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum

class DocumentType(str, enum.Enum):
    QUOTATION = "quotation"
    MOM = "mom"
    WORK_ORDER = "work_order"

class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    REVIEW = "review"
    FINALIZED = "finalized"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    document_type = Column(Enum(DocumentType), nullable=False)
    document_number = Column(String(50), unique=True, index=True)
    title = Column(String(200))
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT)
    original_image_url = Column(String(500))
    ocr_raw_text = Column(Text)
    ocr_confidence = Column(DECIMAL(5, 2))
    final_pdf_url = Column(String(500))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="documents")
    quotation = relationship("Quotation", back_populates="document", uselist=False)
    mom = relationship("MOM", back_populates="document", uselist=False)
    work_order = relationship("WorkOrder", back_populates="document", uselist=False)
