from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from database import SessionLocal, engine
from models import Base, Account, Carrier, Parcel, ScanEvent
from schemas import AccountCreate, CarrierCreate, ParcelCreate, ScanEventCreate

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB Session Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/admin/accounts")
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    if account.tier not in ["free", "pro", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid tier provided")

    new_account = Account(**account.dict())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return {
        "status": "success",
        "account_id": str(new_account.id),
        "message": "Account successfully created"
    }


@app.post("/admin/carriers")
def create_carrier(carrier: CarrierCreate, db: Session = Depends(get_db)):
    existing = db.query(Carrier).filter_by(scac=carrier.scac).first()
    if existing:
        return {
            "status": "exists",
            "carrier_id": str(existing.id),
            "message": "Carrier with this SCAC already exists"
        }

    new_carrier = Carrier(
        id=uuid4(),
        name=carrier.name,
        scac=carrier.scac,
        contact_email=carrier.contact_email,
        active=carrier.active,
    )
    db.add(new_carrier)
    db.commit()
    db.refresh(new_carrier)
    return {
        "status": "success",
        "carrier_id": str(new_carrier.id),
        "message": "Carrier successfully created"
    }



@app.post("/admin/parcel")
def create_parcel(parcel: ParcelCreate, db: Session = Depends(get_db)):
    try:
        print(f"🔍 Incoming Parcel Data: {parcel}")

        existing = db.query(Parcel).filter_by(tracking_id=parcel.tracking_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Parcel already exists")

        new_parcel = Parcel(
            tracking_id=parcel.tracking_id,
            account_id=parcel.account_id,
            carrier_id=parcel.carrier_id,
            origin_region=parcel.origin_region,
            destination_region=parcel.destination_region,
            source_location=parcel.source_location,
            destination_location=parcel.destination_location,
            status="created",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_parcel)
        db.commit()
        db.refresh(new_parcel)

        return {
            "status": "success",
            "tracking_id": new_parcel.tracking_id,
            "message": "Parcel created"
        }

    except HTTPException as e:
        print(f"❌ Error in create_parcel: {e.status_code}: {e.detail}")
        raise e  # re-raise to allow FastAPI to handle it

    except Exception as e:
        print(f"❌ Unexpected error in create_parcel: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/admin/scan")
def log_scan(event: ScanEventCreate, db: Session = Depends(get_db)):
    try:
        # Look up parcel info using tracking_id
        parcel = db.query(Parcel).filter_by(tracking_id=event.tracking_id).first()
        if not parcel:
            raise HTTPException(status_code=404, detail="Parcel not found")

        scan_record = ScanEvent(
            event_id=str(uuid4()),
            tracking_id=event.tracking_id,
            event_type=event.event_type,
            event_ts=event.event_ts,
            facility_region=event.facility_region,
            facility_location=event.facility_location,
            notes=event.notes,
            account_id=parcel.account_id,
            carrier_id=parcel.carrier_id,
            created_at=datetime.utcnow()
        )

        db.add(scan_record)
        db.commit()
        db.refresh(scan_record)

        return {
            "status": "success",
            "event_id": scan_record.event_id,
            "message": "Scan event logged"
        }

    except Exception as e:
        print(f"❌ Unexpected error in log_scan: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



@app.get("/track/{tracking_id}")
def track_parcel(tracking_id: str, db: Session = Depends(get_db)):
    parcel = db.query(Parcel).filter_by(tracking_id=tracking_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    scans = db.query(ScanEvent).filter_by(tracking_id=tracking_id).order_by(ScanEvent.event_ts).all()

    return {
        "tracking_id": tracking_id,
        "status": parcel.status,
        "region": parcel.destination_region,
        "history": [
            {
                "event_type": scan.event_type,
                "event_ts": scan.event_ts,
                "facility_region": scan.facility_region,
                "facility_location": scan.facility_location,
                "notes": scan.notes
            }
            for scan in scans
        ]
    }
