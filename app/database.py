import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

DB_DIR = os.environ.get(
    "LGPD_MANAGER_DB_DIR",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "lgpd_manager.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
