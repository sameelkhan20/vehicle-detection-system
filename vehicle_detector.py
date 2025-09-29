import cv2
import numpy as np
from ultralytics import YOLO
import torch

class VehicleDetector:
    def __init__(self, model_path=None, confidence_threshold=None):
        """
        Initialize the vehicle detector using YOLOv8
        
        Args:
            model_path: Path to YOLOv8 model file
            confidence_threshold: Minimum confidence for detections
        """
        self.model_path = model_path or 'yolov8n.pt'
        self.confidence_threshold = confidence_threshold or 0.5
        
        # Load model
        self.model = YOLO(self.model_path)
        
        # Vehicle class IDs in COCO dataset
        self.vehicle_classes = {
            2: 'car',           # car
            3: 'motorcycle',    # motorcycle
            5: 'bus',           # bus
            7: 'truck'          # truck
        }
        
        # Colors for different vehicle types
        self.colors = {
            'car': (0, 255, 0),         # Green
            'motorcycle': (255, 0, 0),   # Blue
            'bus': (0, 0, 255),         # Red
            'truck': (255, 255, 0)      # Cyan
        }
    
    def detect_vehicles(self, frame):
        """
        Detect vehicles in a frame
        
        Args:
            frame: Input frame (numpy array)
            
        Returns:
            List of detections with format: [x1, y1, x2, y2, confidence, class_id, class_name]
        """
        results = self.model(frame, conf=self.confidence_threshold, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Extract box coordinates and confidence
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Check if it's a vehicle class
                    if class_id in self.vehicle_classes:
                        class_name = self.vehicle_classes[class_id]
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'class_name': class_name
                        })
        return detections
    
    def draw_detections(self, frame, detections, track_ids=None):
        """
        Draw bounding boxes and labels on frame
        
        Args:
            frame: Input frame
            detections: List of detections
            track_ids: Optional list of track IDs for each detection
            
        Returns:
            Frame with drawn detections
        """
        frame_copy = frame.copy()
        
        for i, detection in enumerate(detections):
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            class_name = detection['class_name']
            
            # Get color for vehicle type
            color = self.colors.get(class_name, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)
            
            # Prepare label
            label = f"{class_name}: {confidence:.2f}"
            if track_ids and i < len(track_ids):
                label = f"ID:{track_ids[i]} {label}"
            
            # Draw label background
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame_copy, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(frame_copy, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame_copy
    
    def filter_detections_by_size(self, detections, min_area=1000):
        """
        Filter detections by minimum bounding box area
        
        Args:
            detections: List of detections
            min_area: Minimum area threshold
            
        Returns:
            Filtered list of detections
        """
        filtered = []
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            area = (x2 - x1) * (y2 - y1)
            if area >= min_area:
                filtered.append(detection)
        return filtered
    
    def get_detection_centers(self, detections):
        """
        Get center points of all detections
        
        Args:
            detections: List of detections
            
        Returns:
            List of center points [(x, y), ...]
        """
        centers = []
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            centers.append((center_x, center_y))
        return centers
