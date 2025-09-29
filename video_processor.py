import cv2
import numpy as np
import os
import time
from datetime import datetime

class VideoProcessor:
    def __init__(self, detector, tracker, roi_manager):
        """
        Initialize the video processor
        
        Args:
            detector: VehicleDetector instance
            tracker: VehicleTracker instance
            roi_manager: ROIManager instance
        """
        self.detector = detector
        self.tracker = tracker
        self.roi_manager = roi_manager
        self.frame_count = 0
        self.fps = 30  # Default FPS, will be updated based on input video
    
    def process_video(self, input_path, output_path, log_path, process_id, status_callback):
        """
        Process a video file or RTSP stream
        
        Args:
            input_path: Path to input video or RTSP URL
            output_path: Path to save processed video
            log_path: Path to save CSV log
            process_id: Unique process ID for status updates
            status_callback: Dictionary to update processing status
        """
        try:
            # Open video source
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video source: {input_path}")
            
            # Get video properties
            self.fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))
            
            # Reset counters
            self.frame_count = 0
            self.tracker.reset()
            self.roi_manager.reset_counts()
            
            # Process frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Write processed frame
                out.write(processed_frame)
                
                # Update progress
                self.frame_count += 1
                if total_frames > 0:
                    progress = int((self.frame_count / total_frames) * 100)
                    status_callback[process_id]['progress'] = progress
                    status_callback[process_id]['message'] = f'Processing frame {self.frame_count}/{total_frames}'
                
                # Clean up old tracks periodically
                if self.frame_count % 100 == 0:
                    self.tracker.cleanup_old_tracks()
            
            # Release resources
            cap.release()
            out.release()
            
            # Save logs
            self._save_logs(log_path)
            
            # Final status update
            status_callback[process_id]['message'] = f'Processing completed. Processed {self.frame_count} frames.'
            
        except Exception as e:
            status_callback[process_id]['status'] = 'error'
            status_callback[process_id]['message'] = f'Error during processing: {str(e)}'
            raise
    
    def process_frame(self, frame):
        """
        Process a single frame
        
        Args:
            frame: Input frame
            
        Returns:
            Processed frame with detections, tracks, and counts
        """
        # Detect vehicles
        detections = self.detector.detect_vehicles(frame)
        
        # Filter detections by size (optional)
        detections = self.detector.filter_detections_by_size(detections, min_area=500)
        
        # Update tracker
        tracks = self.tracker.update_tracks(detections, frame)
        
        # Check for ROI crossings
        for track in tracks:
            track_id = track['track_id']
            center = track['center']
            vehicle_type = track['class_name']
            
            # Get track direction (optional)
            direction = self.tracker.get_track_direction(track_id)
            
            # Check if vehicle is crossing counting lines (simplified)
            is_crossing, crossing_direction, line_type = self.roi_manager.check_vehicle_crossing(
                track_id, center, direction, vehicle_type
            )
            
            # Add crossing information to track
            track['is_crossing'] = is_crossing
            track['crossing_direction'] = crossing_direction
            track['line_type'] = line_type
        
        # Draw everything on frame
        processed_frame = self.draw_frame(frame, tracks)
        
        return processed_frame
    
    def draw_frame(self, frame, tracks):
        """
        Draw detections, tracks, and counts on frame
        
        Args:
            frame: Input frame
            tracks: List of active tracks
            
        Returns:
            Frame with all visualizations
        """
        # Start with original frame
        processed_frame = frame.copy()
        
        # Draw ROI and counting lines
        processed_frame = self.roi_manager.draw_roi(processed_frame)
        
        # Draw tracks
        for track in tracks:
            track_id = track['track_id']
            bbox = track['bbox']
            confidence = track['confidence']
            vehicle_type = track['class_name']
            center = track['center']
            
            # Get color based on vehicle type
            colors = {
                'car': (0, 255, 0),
                'motorcycle': (255, 0, 0),
                'bus': (0, 0, 255),
                'truck': (255, 255, 0)
            }
            color = colors.get(vehicle_type, (255, 255, 255))
            
            # Draw bounding box
            x1, y1, x2, y2 = bbox
            cv2.rectangle(processed_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw track ID and vehicle type
            label = f"ID:{track_id} {vehicle_type}"
            if track.get('is_crossing'):
                label += f" ({track.get('crossing_direction', '')})"
            
            # Draw label background
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(processed_frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(processed_frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw center point
            cv2.circle(processed_frame, (int(center[0]), int(center[1])), 3, color, -1)
            
            # Draw direction arrow if available
            direction = self.tracker.get_track_direction(track_id)
            if direction:
                arrow_end = (
                    int(center[0] + direction[0] * 30),
                    int(center[1] + direction[1] * 30)
                )
                cv2.arrowedLine(processed_frame, (int(center[0]), int(center[1])), arrow_end, color, 2)
            
            # Draw speed if available
            speed = self.tracker.calculate_speed(track_id)
            if speed is not None:
                speed_text = f"{speed:.1f} km/h"
                cv2.putText(processed_frame, speed_text, 
                           (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Draw counts
        processed_frame = self.roi_manager.draw_counts(processed_frame)
        
        # Draw frame info
        info_text = f"Frame: {self.frame_count} | Tracks: {len(tracks)}"
        cv2.putText(processed_frame, info_text, 
                   (10, processed_frame.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return processed_frame
    
    def process_rtsp_stream(self, rtsp_url, output_path, log_path, process_id, status_callback, duration=None):
        """
        Process RTSP stream for real-time monitoring
        
        Args:
            rtsp_url: RTSP stream URL
            output_path: Path to save processed video
            log_path: Path to save CSV log
            process_id: Unique process ID for status updates
            status_callback: Dictionary to update processing status
            duration: Maximum duration in seconds (None for continuous)
        """
        try:
            # Open RTSP stream
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                raise ValueError(f"Could not open RTSP stream: {rtsp_url}")
            
            # Get stream properties
            self.fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))
            
            # Reset counters
            self.frame_count = 0
            self.tracker.reset()
            self.roi_manager.reset_counts()
            
            start_time = time.time()
            
            # Process frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    break
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Write processed frame
                out.write(processed_frame)
                
                # Update progress
                self.frame_count += 1
                if self.frame_count % 30 == 0:  # Update every second
                    elapsed_time = time.time() - start_time
                    status_callback[process_id]['progress'] = min(int((elapsed_time / duration) * 100), 99) if duration else 0
                    status_callback[process_id]['message'] = f'Processing RTSP stream - Frame {self.frame_count} - Time: {elapsed_time:.1f}s'
                
                # Clean up old tracks periodically
                if self.frame_count % 100 == 0:
                    self.tracker.cleanup_old_tracks()
            
            # Release resources
            cap.release()
            out.release()
            
            # Save logs
            self._save_logs(log_path)
            
            # Final status update
            status_callback[process_id]['message'] = f'RTSP processing completed. Processed {self.frame_count} frames.'
            
        except Exception as e:
            status_callback[process_id]['status'] = 'error'
            status_callback[process_id]['message'] = f'Error during RTSP processing: {str(e)}'
            raise
    
    def _save_logs(self, log_path):
        """
        Save vehicle crossing logs to a CSV file
        """
        import pandas as pd
        
        entry_log, exit_log = self.roi_manager.get_logs()
        
        # Combine all logs
        all_logs = []
        for log in entry_log + exit_log:
            all_logs.append(log)
        
        if all_logs:
            df = pd.DataFrame(all_logs)
            df.to_csv(log_path, index=False)
            print(f"Logs saved to {log_path}")
        else:
            print("No logs to save.")
