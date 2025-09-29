#!/usr/bin/env python3
"""
Vehicle Detection & Counting System
Startup script for the Flask application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'opencv-python', 'ultralytics', 'numpy', 
        'pandas', 'Pillow', 'deep-sort-realtime', 'torch'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstalling missing packages...")
        install_dependencies()
    else:
        print("✅ All required packages are installed")

def install_dependencies():
    """Install required dependencies"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'outputs', 'static', 'templates']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def check_gpu():
    """Check if GPU is available"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU available: {gpu_name} (Count: {gpu_count})")
        else:
            print("⚠️  GPU not available, using CPU (slower performance)")
    except ImportError:
        print("⚠️  PyTorch not installed, cannot check GPU")

def download_models():
    """Download required models"""
    print("📥 Downloading YOLOv8 model...")
    try:
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        print("✅ YOLOv8 model downloaded")
    except Exception as e:
        print(f"⚠️  Warning: Could not download YOLOv8 model: {e}")
        print("   The model will be downloaded on first use")

def start_application():
    """Start the Flask application"""
    print("\n🚀 Starting Vehicle Detection & Counting System...")
    print("=" * 50)
    print("🌐 Web Interface: http://localhost:5000")
    print("📖 Documentation: See README.md")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🚗 Vehicle Detection & Counting System")
    print("=" * 40)
    
    # Check system requirements
    check_python_version()
    check_dependencies()
    create_directories()
    check_gpu()
    download_models()
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()
