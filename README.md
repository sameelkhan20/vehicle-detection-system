# 🚗 Vehicle Detection and Counting System

A real-time vehicle detection and counting system using YOLOv8, OpenCV, and Flask. This system can detect and track vehicles (cars, trucks, buses, motorcycles) in video streams and count them as they cross a defined Region of Interest (ROI).

## 🌟 Features

- **Real-time Vehicle Detection**: Uses YOLOv8 for accurate vehicle detection
- **Vehicle Tracking**: Custom IoU-based tracker for consistent vehicle tracking
- **ROI-based Counting**: Define a region of interest to count vehicles crossing specific lines
- **Multiple Vehicle Types**: Detects cars, trucks, buses, and motorcycles
- **Video Processing**: Process uploaded videos or RTSP streams
- **CSV Logging**: Export vehicle crossing data to CSV files
- **Speed Estimation**: Calculate vehicle speeds in km/h
- **Web Interface**: Easy-to-use web interface for configuration and monitoring
- **Docker Ready**: Fully containerized for easy deployment

## 🚀 Quick Start

### Option 1: Hugging Face Spaces (Recommended)
1. Fork this repository
2. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
3. Create a new Space with Docker SDK
4. Connect your GitHub repository
5. The app will automatically deploy!

### Option 2: Local Docker
```bash
# Clone the repository
git clone <your-repo-url>
cd vehicle-detection-system

# Build and run with Docker
docker build -t vehicle-detection .
docker run -p 5000:5000 vehicle-detection
```

### Option 3: Local Python
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python start_robust.py
```

## 📖 How to Use

### 1. Upload Video
- Click "Choose File" to upload a video file
- Supported formats: MP4, AVI, MOV, MKV, WMV, FLV, WebM
- Maximum file size: 16MB

### 2. Set Region of Interest (ROI)
- Click "Set ROI" to define the counting area
- Click on the video to create a polygon around the area you want to monitor
- The system will automatically create counting lines (entry/exit) within the ROI

### 3. Process Video
- Click "Process Video" to start processing
- The system will:
  - Detect vehicles in each frame
  - Track vehicles across frames
  - Count vehicles crossing the ROI lines
  - Generate a processed video with bounding boxes and counts
  - Create a CSV log of all vehicle crossings

### 4. Download Results
- Once processing is complete, download:
  - **Processed Video**: Video with detections, tracks, and counts
  - **CSV Log**: Detailed log of vehicle crossings with timestamps

### 5. RTSP Stream (Optional)
- For real-time monitoring, use the RTSP stream option
- Enter your RTSP URL (e.g., `rtsp://your-camera-ip:554/stream`)
- The system will process the live stream and save the results

## 🎯 Vehicle Types Detected

- **Car** (Green bounding box)
- **Motorcycle** (Blue bounding box)  
- **Bus** (Red bounding box)
- **Truck** (Cyan bounding box)

## 📊 Output Information

### Processed Video
- Bounding boxes around detected vehicles
- Vehicle IDs and types
- Direction arrows showing movement
- Speed estimates (when available)
- Real-time count display (IN/OUT)
- ROI polygon and counting lines

### CSV Log
- Timestamp of each vehicle crossing
- Vehicle track ID
- Vehicle type
- Direction (IN/OUT)
- Line type (entry/exit)

## ⚙️ Technical Details

- **Detection Model**: YOLOv8n (nano version for fast processing)
- **Tracking**: Custom IoU-based tracker
- **Confidence Threshold**: 0.5 (adjustable)
- **Minimum Detection Area**: 500 pixels
- **ROI Line Threshold**: 100 pixels
- **Speed Calculation**: Based on pixel movement and frame rate

## 🔧 API Endpoints

- `GET /` - Main interface
- `POST /upload` - Upload video file
- `POST /process` - Start video processing
- `GET /status/<process_id>` - Check processing status
- `GET /download/<process_id>/<file_type>` - Download results
- `POST /set_roi` - Set Region of Interest
- `GET /get_counts` - Get current vehicle counts
- `GET /health` - Health check endpoint

## 🐳 Docker Configuration

The application is fully containerized with:
- **Base Image**: Python 3.9-slim
- **Dependencies**: All required system and Python packages
- **Health Check**: Built-in health monitoring
- **Environment**: Production-ready configuration

## 📁 Project Structure

```
vehicle-detection-system/
├── app.py                 # Main Flask application
├── vehicle_detector.py    # YOLOv8 vehicle detection
├── vehicle_tracker.py     # Custom IoU-based tracking
├── roi_manager.py         # Region of Interest management
├── video_processor.py     # Video processing pipeline
├── start_robust.py        # Robust startup script
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── templates/
│   └── index.html        # Web interface
└── README.md            # This file
```

## 🛠️ Troubleshooting

### Common Issues

**No Vehicles Detected**
- Check if the video quality is good
- Ensure vehicles are clearly visible
- Try adjusting the confidence threshold
- Make sure the ROI is set correctly

**Counting Issues**
- Verify the ROI polygon covers the area where vehicles cross
- Check that counting lines are visible in the processed video
- Ensure vehicles are moving through the ROI area

**Performance Issues**
- Large video files may take longer to process
- RTSP streams require stable network connection
- Processing time depends on video length and resolution

**Permission Errors**
- The app automatically handles permission issues
- Logs are stored in `/tmp` directory
- All directories are created with proper permissions

## 📋 Requirements

- Python 3.9+
- Flask 2.3.3
- OpenCV 4.8.1
- Ultralytics YOLOv8
- PyTorch 2.0.1
- Docker (for containerized deployment)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Create an issue in the repository
3. Check the logs for detailed error information

## 🎉 Acknowledgments

- YOLOv8 by Ultralytics for object detection
- OpenCV for computer vision operations
- Flask for the web framework
- Hugging Face for hosting platform

---

**Ready to deploy!** 🚀 Your vehicle detection system is now fully configured for Hugging Face Spaces deployment.