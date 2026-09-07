import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database URL: uses SQLite locally, or PostgreSQL/MySQL if DATABASE_URL is set in environment (e.g. cloud host)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hospital.db")

# SQLite needs check_same_thread=False for multithreaded FastAPI requests
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Handle Render / Heroku postgresql:// URL prefix fix if postgres
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def run_migrations():
    """Auto-add new columns to existing databases if needed."""
    from sqlalchemy import text
    with engine.connect() as conn:
        for col_def in [
            "ALTER TABLE users ADD COLUMN last_login DATETIME",
            "ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0",
        ]:
            try:
                conn.execute(text(col_def))
                conn.commit()
            except Exception:
                pass

def get_db():
    """Dependency for obtaining a thread-safe database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
