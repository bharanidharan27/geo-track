from database import Base, engine
from models import Account, Carrier, Parcel, ScanEvent

Base.metadata.create_all(bind=engine)