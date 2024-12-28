from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from .database import Base

class WaitlistEntry(Base):
    """SQLAlchemy model for waitlist entries in the database."""
    __tablename__ = "waitlist_entries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    ip_address = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    referral_source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
