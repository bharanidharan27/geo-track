from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

# ----- Account -----
class AccountCreate(BaseModel):
    name: str
    tier: str
    home_region: str
    active: Optional[bool] = True

# ----- Carrier -----
class CarrierCreate(BaseModel):
    name: str
    scac: str
    contact_email: EmailStr
    active: Optional[bool] = True

# ----- Parcel -----
class ParcelCreate(BaseModel):
    tracking_id: str
    account_id: UUID
    carrier_id: UUID
    origin_region: str
    destination_region: str
    source_location: Optional[str] = None
    destination_location: Optional[str] = None

# ----- Scan Event -----
class ScanCreate(BaseModel):
    account_id: UUID
    carrier_id: UUID
    tracking_id: str
    facility_region: str
    facility_location: Optional[str] = None
    event_type: str
    # notes: Optional[str] = None
    event_ts: Optional[datetime] = Field(default_factory=datetime.utcnow)

class ScanEventCreate(BaseModel):
    tracking_id: str
    event_type: str
    event_ts: datetime
    facility_region: str
    facility_location: Optional[str] = None
    # notes: Optional[str] = None