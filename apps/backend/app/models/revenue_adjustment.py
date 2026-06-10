from sqlalchemy import Column, String, DECIMAL, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class RevenueAdjustment(Base):
    __tablename__ = "revenue_adjustments"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(DECIMAL(12, 2), nullable=False)
    date = Column(TIMESTAMP, nullable=False, server_default=func.now())
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="revenue_adjustments")
