from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from .database import Base

class WaitlistEntry(Base):
    """SQLAlchemy model for waitlist entries in the database.
    
    Attributes:
        id (int): Primary key
        name (str): User's full name
        email (str): User's email address (unique)
        ip_address (str): User's IP address
        comment (str): Optional comment from user
        referral_source (str): Where the user came from
        created_at (datetime): When the entry was created (UTC)
        is_active (bool): Whether the entry is active
    """
    __tablename__ = "waitlist_entries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    ip_address = Column(String, nullable=True)
    comment = Column(String, nullable=True)
    referral_source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def to_dict(self) -> dict:
        """Convert the model instance to a dictionary.
        
        Returns:
            dict: Dictionary representation of the waitlist entry
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "ip_address": self.ip_address,
            "comment": self.comment,
            "referral_source": self.referral_source,
            "created_at": self.created_at,
            "is_active": self.is_active
        }
