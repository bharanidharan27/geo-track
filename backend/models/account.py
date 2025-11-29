from sqlalchemy import Column, String, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    tier = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    home_region = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
