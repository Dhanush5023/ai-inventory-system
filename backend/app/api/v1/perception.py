from flask import Blueprint, request, jsonify
import shutil
import os
import uuid
from ...models.database import get_db
from ...ai.anomaly_detection.detector import anomaly_detector
from ...ai.computer_vision.detector import cv_detector
from ...core.security import login_required

bp = Blueprint("perception", __name__)

@bp.route("/anomalies/sales", methods=["GET"])
@login_required
def get_sales_anomalies():
    """Detect anomalies in recent sales data"""
    db = get_db()
    anomalies = anomaly_detector.detect_sales_anomalies(db)
    return jsonify({
        "count": len(anomalies),
        "anomalies": anomalies
    })

@bp.route("/vision/count-stock", methods=["POST"])
@login_required
def count_stock_from_image():
    """Upload an image to count stock items using AI Vision"""
    if 'file' not in request.files:
        return jsonify({"detail": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"detail": "No selected file"}), 400

    # Save temporary file
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
    
    file.save(file_path)
        
    try:
        result = cv_detector.detect_stock(file_path)
        return jsonify(result)
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
