from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://test:vI5vDsj1egBW4ryqvceG8Q@geo-track-17821.j77.cockroachlabs.cloud:26257/geotrack?sslmode=verify-full"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
