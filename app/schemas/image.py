from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# This strictly defines the JSON structure our API will return
class ImageLogResponse(BaseModel):
    id: int
    filename: str
    resolution: str
    status: str
    file_url: Optional[str] = None  # New field for the URL of the saved image
    upload_time: datetime

    class Config:
        # This crucial line tells Pydantic to seamlessly read SQLAlchemy database objects
        from_attributes = True