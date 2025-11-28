from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import uuid4
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parcels_db = {}         # Key: tracking_id, Value: parcel record
scan_events_db = {}     # Key: tracking_id, Value: list of scan events

# Pydantic Models

class AccountCreate(BaseModel):
    name: str
    tier: str  # 'free', 'pro', or 'enterprise'
    home_region: str
    active: Optional[bool] = True

class CarrierCreate(BaseModel):
    name: str
    scac: str
    contact_email: EmailStr
    active: Optional[bool] = True

class ParcelCreate(BaseModel):
    tracking_id: str
    account_id: str
    carrier_id: str
    destination_region: str

class ScanEventCreate(BaseModel):
    tracking_id: str
    event_type: str
    event_ts: str  # ISO format e.g., "2025-11-14T16:00:00"
    facility_region: str
    notes: Optional[str] = None

# Dummy in-memory store
# replace with DB later

accounts_db = {}
carriers_db = {}

# POST /admin/accounts
@app.post("/admin/accounts")
def create_account(account: AccountCreate):
    if account.tier not in ["free", "pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid tier provided")

    account_id = str(uuid4())
    record = {
        "id": account_id,
        "name": account.name,
        "tier": account.tier,
        "home_region": account.home_region,
        "active": account.active,
        "created_at": datetime.utcnow(),
        "crdb_region": account.home_region,
    }
    accounts_db[account_id] = record
    return {
        "status": "success",
        "account_id": account_id,
        "message": "Account successfully created"
    }


# POST /admin/carriers
@app.post("/admin/carriers")
def create_carrier(carrier: CarrierCreate):
    carrier_id = str(uuid4())
    record = {
        "id": carrier_id,
        "name": carrier.name,
        "scac": carrier.scac,
        "contact_email": carrier.contact_email,
        "active": carrier.active,
        "created_at": datetime.utcnow(),
    }
    carriers_db[carrier_id] = record
    return {"status": "success", "carrier_id": carrier_id}

@app.post("/admin/parcel")
def create_parcel(parcel: ParcelCreate):
    if parcel.tracking_id in parcels_db:
        raise HTTPException(status_code=400, detail="Parcel already exists")

    record = {
        "tracking_id": parcel.tracking_id,
        "account_id": parcel.account_id,
        "carrier_id": parcel.carrier_id,
        "destination_region": parcel.destination_region,
        "status": "created",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    parcels_db[parcel.tracking_id] = record
    return {"status": "success", "tracking_id": parcel.tracking_id, "message": "Parcel created"}

@app.post("/admin/scan")
def log_scan(event: ScanEventCreate):
    if event.tracking_id not in parcels_db:
        raise HTTPException(status_code=404, detail="Tracking ID not found")

    scan_record = {
        "event_id": str(uuid4()),
        "tracking_id": event.tracking_id,
        "event_type": event.event_type,
        "event_ts": event.event_ts,
        "facility_region": event.facility_region,
        "notes": event.notes,
        "logged_at": datetime.utcnow().isoformat()
    }

    scan_events_db.setdefault(event.tracking_id, []).append(scan_record)

    return {
        "status": "success",
        "event_id": scan_record["event_id"],
        "message": "Scan event logged"
    }

@app.get("/track/{tracking_id}")
def track_parcel(tracking_id: str):
    if tracking_id not in parcels_db:
        raise HTTPException(status_code=404, detail="Parcel not found")

    parcel = parcels_db[tracking_id]
    scans = scan_events_db.get(tracking_id, [])

    return {
        "tracking_id": tracking_id,
        "status": parcel.get("status", "unknown"),
        "region": parcel.get("destination_region"),
        "history": scans
    }