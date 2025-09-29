#!/usr/bin/env python3
"""
Simple test script to check if the app can start without errors
"""

import sys
import os

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import flask
        print("✓ Flask imported successfully")
        
        import cv2
        print("✓ OpenCV imported successfully")
        
        import numpy as np
        print("✓ NumPy imported successfully")
        
        import pandas as pd
        print("✓ Pandas imported successfully")
        
        import ultralytics
        print("✓ Ultralytics imported successfully")
        
        import torch
        print("✓ PyTorch imported successfully")
        
        # Test our modules
        from vehicle_detector import VehicleDetector
        print("✓ VehicleDetector imported successfully")
        
        from vehicle_tracker import VehicleTracker
        print("✓ VehicleTracker imported successfully")
        
        from roi_manager import ROIManager
        print("✓ ROIManager imported successfully")
        
        from video_processor import VideoProcessor
        print("✓ VideoProcessor imported successfully")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        return False

def test_app_creation():
    """Test if Flask app can be created"""
    try:
        print("\nTesting Flask app creation...")
        
        from app import app
        print("✓ Flask app created successfully")
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                print("✓ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
        
        print("✅ Flask app test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Flask app error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Vehicle Detection System...")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test app creation
    if not test_app_creation():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! The app should work correctly.")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Check the errors above.")
        sys.exit(1)