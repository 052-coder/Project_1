import cv2
import numpy as np

def process_image(contents: bytes) -> tuple[bytes, str]:
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Invalid image file")

    height, width, _ = img.shape
    resolution = f"{width}x{height}"

    processed_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.rectangle(processed_img, (50, 50), (width-50, height-50), (255, 255, 255), 4)

    success, encoded_img = cv2.imencode('.jpg', processed_img)
    if not success:
        raise ValueError("Failed to encode image")

    return encoded_img.tobytes(), resolution