import time
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ImageLog
from app.schemas.image import ImageLogResponse
from app.services.vision import process_image

router = APIRouter()

# Define what we accept
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/jpg"]

# Route 1: Upload and Process
@router.post("/process/")
async def process_and_log(
    request: Request, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # ==========================================
    # 1. THE BOUNCER (Validation)
    # ==========================================
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"File type '{file.content_type}' is not supported. Please upload a JPEG or PNG."
        )

    # ==========================================
    # 2. THE PROCESSING
    # ==========================================
    try:
        contents = await file.read()
        image_bytes, resolution = process_image(contents) 
    except ValueError as e:
        # This catches OpenCV errors (like if a file says it's a JPEG but is actually corrupted)
        raise HTTPException(status_code=400, detail=str(e))
    
    # ==========================================
    # 3. SAVING AND LOGGING
    # ==========================================
    import time
    safe_filename = f"{int(time.time())}_{file.filename}"
    file_path = f"saved_images/{safe_filename}"
    
    with open(file_path, "wb") as f:
        f.write(image_bytes)

    full_url = f"{request.base_url}static/{safe_filename}"
    
    db_log = ImageLog(
        filename=safe_filename, 
        resolution=resolution, 
        status="Processed",
        file_url=full_url
    )
    db.add(db_log)
    db.commit()
    
    return Response(content=image_bytes, media_type="image/jpeg")

# Route 2: Get Logs (Showcasing Pydantic)
# Notice response_model=ImageLogResponse. Pydantic automatically formats the output!
@router.get("/logs/{log_id}", response_model=ImageLogResponse)
def get_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(ImageLog).filter(ImageLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log