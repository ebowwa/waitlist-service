from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import WaitlistEntry
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class WaitlistRepository:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_entry(self, email: str, name: Optional[str] = None, 
                    comment: Optional[str] = None, referral_source: Optional[str] = None) -> WaitlistEntry:
        """Create a new waitlist entry"""
        try:
            entry = WaitlistEntry(
                email=email,
                name=name,
                comment=comment,
                referral_source=referral_source
            )
            self.db.add(entry)
            self.db.commit()
            self.db.refresh(entry)
            return entry
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Email {email} already exists in waitlist")
        except Exception as e:
            self.db.rollback()
            raise
    
    def get_entry_by_email(self, email: str) -> Optional[WaitlistEntry]:
        """Get a waitlist entry by email"""
        return self.db.query(WaitlistEntry).filter(WaitlistEntry.email == email).first()
    
    def get_all_entries(self) -> List[WaitlistEntry]:
        """Get all waitlist entries"""
        return self.db.query(WaitlistEntry).all()
    
    def delete_entry(self, email: str) -> bool:
        """Delete a waitlist entry by email"""
        entry = self.get_entry_by_email(email)
        if entry:
            self.db.delete(entry)
            self.db.commit()
            return True
        return False
