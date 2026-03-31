import cv2
from sqlalchemy.orm import Session
from app.db.models import ImageLog

# This is our Background Task worker
def process_image_background(log_id: int, file_path: str, db: Session):
    try:
        # 1. Read the raw image from the hard drive
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError("Failed to load image for processing")

        height, width, _ = img.shape
        resolution = f"{width}x{height}"

        # 2. The Heavy Lifting (OpenCV)
        processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.rectangle(processed_img, (50, 50), (width-50, height-50), (255, 255, 255), 4)

        # 3. Overwrite the file with the processed version
        cv2.imwrite(file_path, processed_img)

        # 4. Update the Database row to "Processed"
        log = db.query(ImageLog).filter(ImageLog.id == log_id).first()
        if log:
            log.status = "Processed" #type: ignore
            log.resolution = resolution #type: ignore
            db.commit()

    except Exception as e:
        # If OpenCV crashes, mark the database row as "Failed"
        log = db.query(ImageLog).filter(ImageLog.id == log_id).first()
        if log:
            log.status = f"Failed: {str(e)}" #type: ignore
            db.commit()