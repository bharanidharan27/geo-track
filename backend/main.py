from datetime import datetime
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Account, Base, Carrier, Parcel, ScanEvent
from schemas import AccountCreate, CarrierCreate, ParcelCreate, ScanEventCreate

EVENT_DISPLAY_NAMES = {
    "order_submitted": "Order Submitted",
    "label_created": "Label Created",
    "picked_up": "Picked Up",
    "arrived_origin_hub": "Arrived at Origin Hub",
    "departed_origin_hub": "Departed Origin Hub",
    "in_transit": "In Transit",
    "arrived_destination_hub": "Arrived at Destination Hub",
    "arrived_delivery_station": "Arrived at Delivery Station",
    "out_for_delivery": "Out for Delivery",
    "delivered": "Delivered",
    "delay": "Delayed",
    "exception": "Exception",
    "failed_delivery": "Delivery Attempt Failed",
    "rts": "Return to Sender",
    "handoff": "Handed Off",
    "arrival": "Arrival Scan",
    "departure": "Departure Scan",
}

STATUS_BY_EVENT_TYPE = {
    "order_submitted": "created",
    "label_created": "created",
    "picked_up": "in_transit",
    "arrived_origin_hub": "in_transit",
    "departed_origin_hub": "in_transit",
    "in_transit": "in_transit",
    "arrived_destination_hub": "in_transit",
    "arrived_delivery_station": "in_transit",
    "out_for_delivery": "out_for_delivery",
    "delivered": "delivered",
    "delay": "exception",
    "exception": "exception",
    "failed_delivery": "failed_delivery",
    "rts": "rts",
    "handoff": "in_transit",
    "arrival": "in_transit",
    "departure": "in_transit",
}

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def humanize_event_type(event_type: str) -> str:
    return EVENT_DISPLAY_NAMES.get(event_type, event_type.replace("_", " ").title())


def parcel_status_from_event(event_type: str) -> str:
    return STATUS_BY_EVENT_TYPE.get(event_type, "in_transit")


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
        "message": "Account successfully created",
    }


@app.post("/admin/carriers")
def create_carrier(carrier: CarrierCreate, db: Session = Depends(get_db)):
    existing = db.query(Carrier).filter_by(scac=carrier.scac).first()
    if existing:
        return {
            "status": "exists",
            "carrier_id": str(existing.id),
            "message": "Carrier with this SCAC already exists",
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
        "message": "Carrier successfully created",
    }


@app.post("/admin/parcel")
def create_parcel(parcel: ParcelCreate, db: Session = Depends(get_db)):
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
        updated_at=datetime.utcnow(),
    )
    db.add(new_parcel)
    db.commit()
    db.refresh(new_parcel)

    return {
        "status": "success",
        "tracking_id": new_parcel.tracking_id,
        "message": "Parcel created",
    }


@app.post("/admin/scan")
def log_scan(event: ScanEventCreate, db: Session = Depends(get_db)):
    parcel = db.query(Parcel).filter_by(tracking_id=event.tracking_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Tracking ID not found")

    scan_record = ScanEvent(
        event_id=uuid4(),
        tracking_id=event.tracking_id,
        event_type=event.event_type,
        event_ts=event.event_ts,
        facility_region=event.facility_region,
        facility_location=event.facility_location,
        facility_id=event.facility_id,
        facility_type=event.facility_type,
        sequence_no=event.sequence_no,
        journey_stage=event.journey_stage,
        event_message=event.event_message,
        account_id=parcel.account_id,
        carrier_id=parcel.carrier_id,
        created_at=datetime.utcnow(),
    )

    db.add(scan_record)
    parcel.status = parcel_status_from_event(event.event_type)
    parcel.last_event_ts = event.event_ts
    parcel.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(scan_record)

    return {
        "status": "success",
        "event_id": scan_record.event_id,
        "message": "Scan event logged",
    }


@app.get("/track/{tracking_id}")
def track_parcel(tracking_id: str, db: Session = Depends(get_db)):
    parcel = db.query(Parcel).filter_by(tracking_id=tracking_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    scans = db.query(ScanEvent).filter_by(tracking_id=tracking_id).order_by(ScanEvent.event_ts).all()
    latest_status = parcel.status
    if scans:
        latest_status = parcel_status_from_event(scans[-1].event_type)

    return {
        "tracking_id": tracking_id,
        "status": latest_status,
        "region": parcel.destination_region,
        "source_location": parcel.source_location,
        "destination_location": parcel.destination_location,
        "history": [
            {
                "event_type": scan.event_type,
                "event_label": humanize_event_type(scan.event_type),
                "event_ts": scan.event_ts,
                "facility_region": scan.facility_region,
                "facility_location": scan.facility_location,
                "facility_id": scan.facility_id,
                "facility_type": scan.facility_type,
                "sequence_no": scan.sequence_no,
                "journey_stage": scan.journey_stage,
                "event_message": scan.event_message,
            }
            for scan in scans
        ],
    }
