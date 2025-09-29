#!/usr/bin/env python3
"""
Robust startup script for the Vehicle Detection System
Handles all permission issues and provides better error handling
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Set up environment variables to avoid warnings"""
    os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'
    os.environ['YOLO_CONFIG_DIR'] = '/tmp/ultralytics'
    logger.info("✓ Environment variables set")

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import flask
        import cv2
        import numpy
        import pandas
        import ultralytics
        import torch
        logger.info("✓ All dependencies available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def create_directories():
    """Create necessary directories with fallbacks"""
    directories = {
        'uploads': '/app/uploads',
        'outputs': '/app/outputs', 
        'logs': '/tmp/logs',  # Use /tmp for logs to avoid permission issues
        'static': '/app/static',
        'templates': '/app/templates'
    }
    
    for name, path in directories.items():
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"✓ Directory created/verified: {name} -> {path}")
        except Exception as e:
            logger.error(f"❌ Could not create directory {name} at {path}: {e}")
            return False
    
    return True

def start_app():
    """Start the Flask application"""
    try:
        logger.info("🚀 Starting Vehicle Detection System...")
        
        # Set up environment
        setup_environment()
        
        # Check dependencies
        if not check_dependencies():
            logger.error("❌ Dependencies check failed")
            return False
        
        # Create directories
        if not create_directories():
            logger.error("❌ Directory creation failed")
            return False
        
        # Import and start the app
        from app import app
        
        logger.info("✓ Flask app imported successfully")
        logger.info("✓ Starting server on http://0.0.0.0:5000")
        
        # Start the app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Set to False for production
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start app: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚗 Vehicle Detection System Startup (Robust Version)")
    logger.info(f"⏰ Started at: {datetime.now()}")
    logger.info("=" * 60)
    
    success = start_app()
    
    if not success:
        logger.error("💥 Application failed to start")
        sys.exit(1)
