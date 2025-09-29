import numpy as np
import cv2
from collections import defaultdict
import math

class VehicleTracker:
    def __init__(self, max_age=None, n_init=None, max_iou_distance=None):
        """
        Initialize the vehicle tracker using a simple IoU-based tracker
        
        Args:
            max_age: Maximum number of frames to keep a track without detections
            n_init: Number of consecutive detections before a track is confirmed
            max_iou_distance: Maximum IoU distance for association
        """
        self.max_age = max_age or 30
        self.n_init = n_init or 3
        self.max_iou_distance = max_iou_distance or 0.7
        
        # Simple tracking state
        self.tracks = {}
        self.next_id = 1
        self.track_history = {}  # Store track history for each ID
        self.speed_history = {}  # Store speed history for each ID
        self.frame_count = 0
    
    def update_tracks(self, detections, frame):
        """
        Update tracks with new detections using simple IoU-based tracking
        
        Args:
            detections: List of detections from detector
            frame: Current frame for feature extraction
            
        Returns:
            List of tracks with format: [track_id, bbox, confidence, class_name]
        """
        self.frame_count += 1
        
        # Convert detections to our format
        current_detections = []
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            confidence = det['confidence']
            class_name = det['class_name']
            
            current_detections.append({
                'bbox': [x1, y1, x2, y2],
                'confidence': confidence,
                'class_name': class_name,
                'center': ((x1 + x2) / 2, (y1 + y2) / 2)
            })
        
        # Update existing tracks
        self._update_existing_tracks(current_detections)
        
        # Create new tracks for unmatched detections
        self._create_new_tracks(current_detections)
        
        # Remove old tracks
        self._remove_old_tracks()
        
        # Return active tracks
        active_tracks = []
        for track_id, track in self.tracks.items():
            if track['age'] < self.max_age and track['hits'] >= self.n_init:
                active_tracks.append({
                    'track_id': track_id,
                    'bbox': track['bbox'],
                    'confidence': track['confidence'],
                    'class_name': track['class_name'],
                    'center': track['center']
                })
        
        return active_tracks
    
    def _update_existing_tracks(self, detections):
        """Update existing tracks with new detections"""
        # Calculate IoU matrix between tracks and detections
        iou_matrix = self._calculate_iou_matrix(detections)
        
        # Associate tracks with detections
        matched_tracks, matched_detections = self._associate_tracks(iou_matrix)
        
        # Update matched tracks
        for track_idx, det_idx in zip(matched_tracks, matched_detections):
            track_id = list(self.tracks.keys())[track_idx]
            detection = detections[det_idx]
            
            # Update track
            self.tracks[track_id]['bbox'] = detection['bbox']
            self.tracks[track_id]['confidence'] = detection['confidence']
            self.tracks[track_id]['class_name'] = detection['class_name']
            self.tracks[track_id]['center'] = detection['center']
            self.tracks[track_id]['hits'] += 1
            self.tracks[track_id]['age'] = 0
            
            # Update track history
            if track_id not in self.track_history:
                self.track_history[track_id] = []
            
            self.track_history[track_id].append({
                'frame': self.frame_count,
                'center': detection['center'],
                'bbox': detection['bbox'],
                'confidence': detection['confidence'],
                'class_name': detection['class_name'],
                'timestamp': self.frame_count
            })
            
            # Keep only recent history
            if len(self.track_history[track_id]) > 30:
                self.track_history[track_id] = self.track_history[track_id][-30:]
        
        # Age unmatched tracks
        for track_id, track in self.tracks.items():
            if track_id not in [list(self.tracks.keys())[i] for i in matched_tracks]:
                track['age'] += 1
    
    def _create_new_tracks(self, detections):
        """Create new tracks for unmatched detections"""
        # Calculate IoU matrix to find unmatched detections
        iou_matrix = self._calculate_iou_matrix(detections)
        matched_detections = set()
        
        if iou_matrix.size > 0:
            # Find matched detections
            for i in range(iou_matrix.shape[0]):
                best_j = np.argmax(iou_matrix[i])
                if iou_matrix[i, best_j] > self.max_iou_distance:
                    matched_detections.add(best_j)
        
        # Create new tracks for unmatched detections
        for i, detection in enumerate(detections):
            if i not in matched_detections:
                track_id = self.next_id
                self.next_id += 1
                
                self.tracks[track_id] = {
                    'bbox': detection['bbox'],
                    'confidence': detection['confidence'],
                    'class_name': detection['class_name'],
                    'center': detection['center'],
                    'hits': 1,
                    'age': 0
                }
    
    def _remove_old_tracks(self):
        """Remove tracks that are too old"""
        tracks_to_remove = []
        for track_id, track in self.tracks.items():
            if track['age'] > self.max_age:
                tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.tracks[track_id]
            if track_id in self.track_history:
                del self.track_history[track_id]
    
    def _calculate_iou_matrix(self, detections):
        """Calculate IoU matrix between tracks and detections"""
        if not self.tracks or not detections:
            return np.array([])
        
        iou_matrix = np.zeros((len(self.tracks), len(detections)))
        
        for i, track in enumerate(self.tracks.values()):
            for j, detection in enumerate(detections):
                iou_matrix[i, j] = self._calculate_iou(track['bbox'], detection['bbox'])
        
        return iou_matrix
    
    def _calculate_iou(self, bbox1, bbox2):
        """Calculate Intersection over Union (IoU) of two bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _associate_tracks(self, iou_matrix):
        """Associate tracks with detections using Hungarian algorithm (simplified)"""
        if iou_matrix.size == 0:
            return [], []
        
        # Simple greedy association
        matched_tracks = []
        matched_detections = []
        
        # Find best matches above threshold
        for i in range(iou_matrix.shape[0]):
            best_j = np.argmax(iou_matrix[i])
            if iou_matrix[i, best_j] > self.max_iou_distance:
                if best_j not in matched_detections:
                    matched_tracks.append(i)
                    matched_detections.append(best_j)
        
        return matched_tracks, matched_detections
    
    
    def calculate_speed(self, track_id, pixels_per_meter=None):
        """
        Calculate speed for a track in km/h
        
        Args:
            track_id: ID of the track
            pixels_per_meter: Conversion factor from pixels to meters
            
        Returns:
            Speed in km/h, or None if not enough data
        """
        if pixels_per_meter is None:
            pixels_per_meter = 10
            
        if track_id not in self.track_history or len(self.track_history[track_id]) < 2:
            return None
        
        history = self.track_history[track_id]
        
        # Use last 5 positions for speed calculation
        recent_positions = history[-5:]
        
        if len(recent_positions) < 2:
            return None
        
        # Calculate total distance moved
        total_distance = 0
        for i in range(1, len(recent_positions)):
            prev_center = recent_positions[i-1]['center']
            curr_center = recent_positions[i]['center']
            
            distance = np.sqrt(
                (curr_center[0] - prev_center[0])**2 + 
                (curr_center[1] - prev_center[1])**2
            )
            total_distance += distance
        
        # Calculate time elapsed (assuming 30 FPS)
        time_elapsed = (len(recent_positions) - 1) / 30.0  # seconds
        
        if time_elapsed == 0:
            return None
        
        # Convert to real-world units
        distance_meters = total_distance / pixels_per_meter
        speed_mps = distance_meters / time_elapsed
        speed_kmh = speed_mps * 3.6
        
        return speed_kmh
    
    def get_track_direction(self, track_id):
        """
        Get the direction of movement for a track
        
        Args:
            track_id: ID of the track
            
        Returns:
            Direction vector (dx, dy) or None if not enough data
        """
        if track_id not in self.track_history or len(self.track_history[track_id]) < 2:
            return None
        
        history = self.track_history[track_id]
        recent = history[-3:]  # Use last 3 positions
        
        if len(recent) < 2:
            return None
        
        # Calculate average direction
        dx_total = 0
        dy_total = 0
        
        for i in range(1, len(recent)):
            prev_center = recent[i-1]['center']
            curr_center = recent[i]['center']
            
            dx_total += curr_center[0] - prev_center[0]
            dy_total += curr_center[1] - prev_center[1]
        
        # Normalize direction
        dx_avg = dx_total / (len(recent) - 1)
        dy_avg = dy_total / (len(recent) - 1)
        
        # Normalize to unit vector
        magnitude = np.sqrt(dx_avg**2 + dy_avg**2)
        if magnitude > 0:
            return (dx_avg / magnitude, dy_avg / magnitude)
        
        return None
    
    def is_track_crossing_line(self, track_id, line_start, line_end, direction_threshold=0.1):
        """
        Check if a track is crossing a line (for ROI counting)
        
        Args:
            track_id: ID of the track
            line_start: Start point of the line (x, y)
            line_end: End point of the line (x, y)
            direction_threshold: Minimum direction component for crossing detection
            
        Returns:
            Tuple of (is_crossing, crossing_direction) where direction is 'in' or 'out'
        """
        if track_id not in self.track_history or len(self.track_history[track_id]) < 2:
            return False, None
        
        history = self.track_history[track_id]
        recent = history[-3:]  # Use last 3 positions
        
        if len(recent) < 2:
            return False, None
        
        # Check if track crossed the line
        prev_center = recent[0]['center']
        curr_center = recent[-1]['center']
        
        # Calculate which side of the line each point is on
        def point_side_of_line(point, line_start, line_end):
            return ((line_end[0] - line_start[0]) * (point[1] - line_start[1]) - 
                   (line_end[1] - line_start[1]) * (point[0] - line_start[0]))
        
        prev_side = point_side_of_line(prev_center, line_start, line_end)
        curr_side = point_side_of_line(curr_center, line_start, line_end)
        
        # Check if line was crossed
        if prev_side * curr_side < 0:  # Different sides
            # Determine direction based on movement
            direction = self.get_track_direction(track_id)
            if direction:
                # Project direction onto line normal
                line_vec = (line_end[0] - line_start[0], line_end[1] - line_start[1])
                line_length = np.sqrt(line_vec[0]**2 + line_vec[1]**2)
                if line_length > 0:
                    line_normal = (-line_vec[1] / line_length, line_vec[0] / line_length)
                    dot_product = direction[0] * line_normal[0] + direction[1] * line_normal[1]
                    
                    if dot_product > direction_threshold:
                        return True, 'in'
                    elif dot_product < -direction_threshold:
                        return True, 'out'
        
        return False, None
    
    def cleanup_old_tracks(self, max_age=100):
        """
        Remove old tracks from history
        
        Args:
            max_age: Maximum age of tracks to keep
        """
        current_frame = self.frame_count
        tracks_to_remove = []
        
        for track_id, history in self.track_history.items():
            if history and current_frame - history[-1]['frame'] > max_age:
                tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.track_history[track_id]
            if track_id in self.speed_history:
                del self.speed_history[track_id]
    
    def get_track_count(self):
        """Get the number of active tracks"""
        return len(self.track_history)
    
    def reset(self):
        """Reset the tracker"""
        self.tracks = {}
        self.next_id = 1
        self.track_history = {}
        self.speed_history = {}
        self.frame_count = 0
