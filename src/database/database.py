from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from .models import Base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def setup_database() -> tuple:
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in the environment variables.")

    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    return engine, SessionLocal
