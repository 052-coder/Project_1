from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.db.database import Base

class ImageLog(Base):
    __tablename__ = "image_logs"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    resolution = Column(String)
    status = Column(String)
    file_url = Column(String, nullable=True)  # New column to store the URL of the saved image
    upload_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))