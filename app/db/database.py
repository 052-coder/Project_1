from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Format: postgresql://username:password@host:port/database_name
# Replace "your_password" with your actual Postgres password
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:root@localhost:5432/vision_db"

# Postgres doesn't need the check_same_thread argument
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()