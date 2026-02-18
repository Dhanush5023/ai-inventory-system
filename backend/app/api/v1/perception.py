from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os
import uuid
from ...models.database import get_db
from ...ai.anomaly_detection.detector import anomaly_detector
from ...ai.computer_vision.detector import cv_detector
from ...core.security import get_current_user_id

router = APIRouter()

@router.get("/anomalies/sales")
def get_sales_anomalies(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Detect anomalies in recent sales data"""
    anomalies = anomaly_detector.detect_sales_anomalies(db)
    return {
        "count": len(anomalies),
        "anomalies": anomalies
    }

@router.post("/vision/count-stock")
async def count_stock_from_image(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id)
):
    """Upload an image to count stock items using AI Vision"""
    # Save temporary file
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        result = cv_detector.detect_stock(file_path)
        return result
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
