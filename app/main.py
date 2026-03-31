import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import upload
from app.db.database import engine, Base

# Create a folder on your computer to hold the saved images
os.makedirs("saved_images", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Structured Vision API")

# Mount the folder to a web URL. 
# Now, anything in the "saved_images" folder can be viewed at /static/...
app.mount("/static", StaticFiles(directory="saved_images"), name="static")

app.include_router(upload.router, prefix="/api")