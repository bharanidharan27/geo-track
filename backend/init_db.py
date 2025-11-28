from database import Base, engine
from models.account import Account

Base.metadata.create_all(bind=engine)
