from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import base as pg_base

# ✅ Force version fallback BEFORE engine initialization
def _patched_get_server_version_info(self, connection):
    return (12, 0)  # Fake PostgreSQL-compatible version

pg_base.PGDialect._get_server_version_info = _patched_get_server_version_info

# ✅ Regular SQLAlchemy CockroachDB URL using psycopg2
DATABASE_URL = "postgresql+psycopg2://test:vI5vDsj1egBW4ryqvceG8Q@geo-track-17821.j77.cockroachlabs.cloud:26257/geotrack?sslmode=verify-full"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
