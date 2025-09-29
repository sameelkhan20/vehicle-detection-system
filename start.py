#!/usr/bin/env python3
"""
Startup script for the Vehicle Detection System
Handles errors gracefully and provides better logging
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
    """Create necessary directories"""
    directories = ['uploads', 'outputs', 'logs', 'static', 'templates']
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✓ Directory created/verified: {directory}")
        except PermissionError as e:
            logger.warning(f"⚠️ Could not create directory {directory}: {e}")
            # Try to create in /tmp instead
            if directory == 'logs':
                temp_logs = '/tmp/logs'
                try:
                    os.makedirs(temp_logs, exist_ok=True)
                    logger.info(f"✓ Created logs directory in /tmp: {temp_logs}")
                except Exception as e2:
                    logger.error(f"❌ Could not create logs directory anywhere: {e2}")
            else:
                logger.error(f"❌ Could not create directory {directory}: {e}")

def start_app():
    """Start the Flask application"""
    try:
        logger.info("🚀 Starting Vehicle Detection System...")
        
        # Check dependencies
        if not check_dependencies():
            logger.error("❌ Dependencies check failed")
            return False
        
        # Create directories
        create_directories()
        
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
        return False

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚗 Vehicle Detection System Startup")
    logger.info(f"⏰ Started at: {datetime.now()}")
    logger.info("=" * 60)
    
    success = start_app()
    
    if not success:
        logger.error("💥 Application failed to start")
        sys.exit(1)
