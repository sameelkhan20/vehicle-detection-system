"""
Configuration settings for the Vehicle Detection & Counting System
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / 'uploads'
OUTPUT_FOLDER = BASE_DIR / 'outputs'
STATIC_FOLDER = BASE_DIR / 'static'
TEMPLATE_FOLDER = BASE_DIR / 'templates'

# Flask configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    UPLOAD_FOLDER = str(UPLOAD_FOLDER)
    OUTPUT_FOLDER = str(OUTPUT_FOLDER)
    
    # Video processing settings
    SUPPORTED_VIDEO_FORMATS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}
    DEFAULT_FPS = 30
    
    # Detection settings
    YOLO_MODEL_PATH = 'yolov8n.pt'  # Options: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
    CONFIDENCE_THRESHOLD = 0.3  # Lowered for better detection
    MIN_DETECTION_AREA = 200  # Lowered for smaller vehicles
    
    # Tracking settings
    MAX_AGE = 30  # Maximum frames to keep track without detection
    N_INIT = 3    # Frames needed to confirm track
    MAX_IOU_DISTANCE = 0.7  # Maximum IoU distance for association
    
    # ROI settings
    ROI_LINE_THRESHOLD = 100  # Distance threshold for line crossing detection (increased for better detection)
    DIRECTION_THRESHOLD = 0.1  # Minimum direction component for crossing detection
    
    # Speed estimation
    PIXELS_PER_METER = 10  # Conversion factor from pixels to meters
    SPEED_CALCULATION_FRAMES = 5  # Number of recent frames for speed calculation
    
    # Logging settings
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = 'INFO'
    
    # Performance settings
    CLEANUP_INTERVAL = 100  # Frames between track cleanup
    MAX_TRACK_HISTORY = 30  # Maximum frames to keep in track history

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Add production-specific settings here

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Vehicle class mappings
VEHICLE_CLASSES = {
    2: 'car',           # car
    3: 'motorcycle',    # motorcycle
    5: 'bus',           # bus
    7: 'truck'          # truck
}

# Colors for different vehicle types
VEHICLE_COLORS = {
    'car': (0, 255, 0),         # Green
    'motorcycle': (255, 0, 0),   # Blue
    'bus': (0, 0, 255),         # Red
    'truck': (255, 255, 0)      # Cyan
}

# RTSP settings
RTSP_TIMEOUT = 30  # seconds
RTSP_RETRY_ATTEMPTS = 3

# File upload settings
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}

# Database settings (for future use)
DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///vehicle_detection.db'

# Redis settings (for future use)
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

# Cloud storage settings (for future use)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
