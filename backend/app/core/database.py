import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv

# Load local .env for development. In Railway, env vars are provided by the platform.
load_dotenv()

# Prefer DATABASE_URL from environment; fallback to local SQLite for dev.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./musicscope.db")

# Some platforms provide `postgres://` but SQLAlchemy expects `postgresql://`
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()