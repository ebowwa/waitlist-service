from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class WaitlistEntryBase(BaseModel):
    name: str
    email: EmailStr
    comment: Optional[str] = None
    referral_source: Optional[str] = None

class WaitlistCreate(WaitlistEntryBase):
    pass

class WaitlistUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    comment: Optional[str] = None
    referral_source: Optional[str] = None

class WaitlistEntry(WaitlistEntryBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[int] = None
    ip_address: Optional[str]
    created_at: Optional[datetime] = None
