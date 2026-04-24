from sqlalchemy import Column, String, Boolean, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    company_name = Column(String(200))
    company_logo_url = Column(String(500))
    phone = Column(String(20))
    address = Column(Text)
    gst_number = Column(String(20))
    default_terms_conditions = Column(Text)
    is_admin = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    documents = relationship("Document", back_populates="user", lazy="dynamic")
    products = relationship("Product", back_populates="user", lazy="dynamic")
