from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import json
import uuid
from werkzeug.utils import secure_filename
import threading
import time
import logging

from vehicle_detector import VehicleDetector
from vehicle_tracker import VehicleTracker
from roi_manager import ROIManager
from video_processor import VideoProcessor

# Create Flask app
app = Flask(__name__)

# Load configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['LOG_FOLDER'] = 'logs'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Try to create logs directory, fallback to /tmp if permission denied
try:
    os.makedirs(app.config['LOG_FOLDER'], exist_ok=True)
except PermissionError:
    app.config['LOG_FOLDER'] = '/tmp/logs'
    os.makedirs(app.config['LOG_FOLDER'], exist_ok=True)
    logging.warning(f"Could not create logs directory, using {app.config['LOG_FOLDER']} instead")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Global variables for processing
processing_status = {}
detector = None
tracker = None
roi_manager = None

def initialize_models():
    global detector, tracker, roi_manager
    try:
        detector = VehicleDetector()
        tracker = VehicleTracker()
        roi_manager = ROIManager()
        logging.info("Models initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing models: {e}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'filename': filename, 'message': 'File uploaded successfully'})
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/process', methods=['POST'])
def process_video():
    data = request.get_json()
    filename = data.get('filename')
    roi_points = data.get('roi_points', [])
    process_type = data.get('process_type', 'upload')  # 'upload' or 'rtsp'
    rtsp_url = data.get('rtsp_url', '')

    if not filename and process_type == 'upload':
        return jsonify({'error': 'No filename provided'}), 400

    if process_type == 'rtsp' and not rtsp_url:
        return jsonify({'error': 'No RTSP URL provided'}), 400

    # Generate unique processing ID
    process_id = str(uuid.uuid4())
    processing_status[process_id] = {
        'status': 'processing',
        'progress': 0,
        'message': 'Starting processing...',
        'output_file': None,
        'log_file': None
    }

    # Start processing in a separate thread
    thread = threading.Thread(
        target=process_video_thread,
        args=(process_id, filename, roi_points, process_type, rtsp_url)
    )
    thread.start()

    return jsonify({'process_id': process_id, 'message': 'Processing started'})

def process_video_thread(process_id, filename, roi_points, process_type, rtsp_url):
    try:
        if detector is None or tracker is None or roi_manager is None:
            initialize_models()

        video_processor = VideoProcessor(detector, tracker, roi_manager)

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) if process_type == 'upload' else rtsp_url
        output_filename = f"processed_{os.path.splitext(filename)[0]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4" if process_type == 'upload' else f"processed_rtsp_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        log_filename = f"log_{os.path.splitext(filename)[0]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv" if process_type == 'upload' else f"log_rtsp_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        log_path = os.path.join(app.config['LOG_FOLDER'], log_filename)

        roi_manager.set_roi(roi_points)

        if process_type == 'upload':
            video_processor.process_video(input_path, output_path, log_path, process_id, processing_status)
        else:
            video_processor.process_rtsp_stream(input_path, output_path, log_path, process_id, processing_status)

        processing_status[process_id].update({
            'status': 'completed',
            'progress': 100,
            'message': 'Processing completed successfully',
            'output_file': output_path,
            'log_file': log_path,
            'counts': roi_manager.get_counts()
        })
    except Exception as e:
        logging.error(f"Error processing video {process_id}: {e}", exc_info=True)
        processing_status[process_id].update({
            'status': 'error',
            'message': f'Processing failed: {str(e)}',
            'progress': 0
        })

@app.route('/status/<process_id>')
def get_status(process_id):
    status = processing_status.get(process_id, {'status': 'not_found', 'message': 'Process ID not found'})
    return jsonify(status)

@app.route('/download/<process_id>/<file_type>')
def download_file(process_id, file_type):
    status = processing_status.get(process_id)
    if not status or status['status'] != 'completed':
        return jsonify({'error': 'Processing not completed or ID not found'}), 404

    if file_type == 'video' and status.get('output_file'):
        return send_file(status['output_file'], as_attachment=True)
    elif file_type == 'log' and status.get('log_file'):
        return send_file(status['log_file'], as_attachment=True)

    return jsonify({'error': 'File not found'}), 404

@app.route('/set_roi', methods=['POST'])
def set_roi():
    data = request.get_json()
    roi_points = data.get('roi_points', [])

    if len(roi_points) < 3:
        return jsonify({'error': 'At least 3 points required for ROI'}), 400

    if roi_manager is None:
        initialize_models()

    roi_manager.set_roi(roi_points)

    return jsonify({'success': True, 'message': 'ROI set successfully'})

@app.route('/get_counts')
def get_counts():
    """Get current vehicle counts"""
    if roi_manager is None:
        return jsonify({'error': 'ROI manager not initialized'}), 400

    counts = roi_manager.get_counts()
    return jsonify(counts)

@app.route('/health')
def health_check():
    """Health check endpoint for Docker"""
    return jsonify({'status': 'healthy', 'message': 'Vehicle detection system is running'})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    # Don't initialize models at startup to avoid runtime errors
    # Models will be initialized when first needed
    app.run(debug=True, host='0.0.0.0', port=5000)