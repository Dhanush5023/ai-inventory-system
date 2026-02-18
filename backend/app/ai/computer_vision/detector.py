from typing import Dict, List, Any
import os

try:
    import cv2
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] Vision libraries unavailable: {e}")
    ULTRALYTICS_AVAILABLE = False
import numpy as np

class StockVisionDetector:
    """Computer Vision service for automated stock counting using YOLOv8"""
    
    def __init__(self, model_name: str = "yolov8n.pt"):
        # Load pre-trained nano model (will download on first run)
        if not ULTRALYTICS_AVAILABLE:
            self.model = None
            return
            
        try:
            self.model = YOLO(model_name)
        except Exception as e:
            print(f"CV Model Error: {e}")
            self.model = None

    def detect_stock(self, image_path: str) -> Dict[str, Any]:
        """Detect and count items in an image"""
        if not self.model:
            return {"error": "CV Model not initialized", "count": 0}
            
        if not os.path.exists(image_path):
            return {"error": "Image path not found", "count": 0}
            
        results = self.model(image_path)
        
        # Count objects (YOLO results are a list of boxes)
        # For demo, we treat everything detected as 'stock item'
        # In real scenario, we'd filter by class IDs (e.g., box, bottle)
        item_count = len(results[0].boxes)
        
        detected_items = []
        for box in results[0].boxes:
            detected_items.append({
                "class": self.model.names[int(box.cls)],
                "confidence": float(box.conf),
                "box": box.xyxy.tolist()[0]
            })
            
        return {
            "item_count": item_count,
            "detected_objects": detected_items,
            "message": f"Successfully detected {item_count} items."
        }

# Global instance
cv_detector = StockVisionDetector()
