from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, get_db
from app.db.models import ImageLog
from app.services.vision import process_image_background
from app.schemas.image import ImageLogResponse
import time

router = APIRouter()
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/jpg"]

# We need a dedicated database session for the background task
def get_background_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

@router.post("/process/")
async def process_and_log(
    request: Request,
    background_tasks: BackgroundTasks, # <--- NEW: Inject BackgroundTasks
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # 1. The Bouncer
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    # 2. Save the RAW, unprocessed file instantly
    safe_filename = f"{int(time.time())}_{file.filename}"
    file_path = f"saved_images/{safe_filename}"
    
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # 3. Create a "Pending" log in the database
    full_url = f"{request.base_url}static/{safe_filename}"
    db_log = ImageLog(
        filename=safe_filename, 
        resolution="Pending...", 
        status="Processing", # <--- Notice the status!
        file_url=full_url
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log) # Get the generated ID

    # 4. Kick off the heavy OpenCV task in the background
    bg_db = get_background_db()
    background_tasks.add_task(process_image_background, db_log.id, file_path, bg_db) # type: ignore

    # 5. Return a response immediately! Don't wait for OpenCV.
    return {
        "message": "Image accepted and is processing in the background.",
        "log_id": db_log.id,
        "status": "Processing",
        "check_status_url": f"{request.base_url}api/logs/{db_log.id}"
    }

# Route 2: Get Logs (Showcasing Pydantic)
# Notice response_model=ImageLogResponse. Pydantic automatically formats the output!
@router.get("/logs/{log_id}", response_model=ImageLogResponse)
def get_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(ImageLog).filter(ImageLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log