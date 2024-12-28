from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class WaitlistEntry(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    ip_address = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    referral_source = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
