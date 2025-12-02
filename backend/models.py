from sqlalchemy import Column, String, Boolean, TIMESTAMP, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base
import uuid

# --------------------- Accounts ---------------------
class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    tier = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    home_region = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("tier IN ('free', 'pro', 'enterprise')", name='tier_check'),
    )

# --------------------- Carriers ---------------------
class Carrier(Base):
    __tablename__ = "carriers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    scac = Column(String, nullable=False, unique=True)
    contact_email = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

# --------------------- Parcels ---------------------
class Parcel(Base):
    __tablename__ = "parcels"

    tracking_id = Column(String, primary_key=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    carrier_id = Column(UUID(as_uuid=True), ForeignKey("carriers.id"), nullable=False)
    source_location = Column(String, nullable=True)
    destination_location = Column(String, nullable=True)
    origin_region = Column(String, nullable=False)
    destination_region = Column(String, nullable=False)
    status = Column(String, default="created")
    last_event_ts = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('created', 'in_transit', 'out_for_delivery', 'delivered')", name='status_check'),
    )

# --------------------- Scan Events ---------------------
class ScanEvent(Base):
    __tablename__ = "scan_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    carrier_id = Column(UUID(as_uuid=True), ForeignKey("carriers.id"), nullable=False)
    tracking_id = Column(String, ForeignKey("parcels.tracking_id"), nullable=False)
    event_ts = Column(TIMESTAMP(timezone=True), nullable=False)
    facility_region = Column(String, nullable=False)
    facility_location = Column(String, nullable=True)
    event_type = Column(String, nullable=False)
    # notes = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("tracking_id", "event_ts", "event_type", "facility_region", name="dedup_index"),
        CheckConstraint(
            "event_type IN ('handoff', 'arrival', 'departure', 'out_for_delivery', 'delivered', 'exception', 'rts')",
            name="event_type_check"
        ),
    )
