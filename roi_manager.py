import numpy as np
import cv2
from datetime import datetime

class ROIManager:
    def __init__(self):
        """
        Initialize the Region of Interest manager for vehicle counting
        """
        self.roi_points = []
        self.roi_polygon = None
        self.counting_lines = []
        self.vehicle_counts = {
            'total_in': 0,
            'total_out': 0,
            'by_type': {}
        }
        self.crossed_vehicles = set()  # Track which vehicles have already been counted
        self.entry_log = []
        self.exit_log = []
        self.line_threshold = 100  # Default value
        self.direction_threshold = 0.1  # Default value
    
    def set_roi(self, points):
        """
        Set the Region of Interest polygon
        
        Args:
            points: List of [x, y] coordinates defining the ROI polygon
        """
        if len(points) < 3:
            raise ValueError("At least 3 points required for ROI polygon")
        
        self.roi_points = points
        self.roi_polygon = np.array(points, dtype=np.int32)
        
        # Reset counts and crossed vehicles when ROI is set
        self.reset_counts()
        
        # Generate counting lines
        self._generate_counting_lines()
    
    def _generate_counting_lines(self):
        """
        Generate counting lines for vehicle detection
        """
        if len(self.roi_points) < 3:
            return
        
        # Create a simple horizontal line across the ROI center
        # This will work for most traffic scenarios
        min_x = min(point[0] for point in self.roi_points)
        max_x = max(point[0] for point in self.roi_points)
        min_y = min(point[1] for point in self.roi_points)
        max_y = max(point[1] for point in self.roi_points)
        
        center_y = (min_y + max_y) / 2
        
        # Create two horizontal lines - one above and one below center
        line1_y = center_y - 30  # Entry line (above center)
        line2_y = center_y + 30  # Exit line (below center)
        
        self.counting_lines = [
            {
                'start': [int(min_x), int(line1_y)],
                'end': [int(max_x), int(line1_y)],
                'type': 'entry'
            },
            {
                'start': [int(min_x), int(line2_y)],
                'end': [int(max_x), int(line2_y)],
                'type': 'exit'
            }
        ]
        
    
    def is_point_in_roi(self, point):
        """
        Check if a point is inside the ROI polygon
        
        Args:
            point: (x, y) coordinates
            
        Returns:
            True if point is inside ROI
        """
        if self.roi_polygon is None:
            return True  # If no ROI set, consider all points valid
        
        return cv2.pointPolygonTest(self.roi_polygon, point, False) >= 0
    
    def check_vehicle_crossing(self, track_id, center_point, direction, vehicle_type):
        """
        Check if a vehicle is crossing a counting line
        
        Args:
            track_id: ID of the vehicle track
            center_point: Current center point of the vehicle
            direction: Direction vector of movement
            vehicle_type: Type of vehicle
            
        Returns:
            Tuple of (is_crossing, crossing_type, line_type)
        """
        if not self.counting_lines:
            return False, None, None
        
        # Check if vehicle is already counted (prevent double counting)
        if track_id in self.crossed_vehicles:
            return False, None, None
        
        # Simple crossing detection based on line proximity
        for line in self.counting_lines:
            # Calculate distance to line
            distance = self._point_to_line_distance(center_point, line['start'], line['end'])
            
            # If vehicle is close to line, count it
            if distance < self.line_threshold:
                # Determine direction based on line type
                if line['type'] == 'entry':
                    crossing_direction = 'in'
                    line_type = 'entry'
                else:
                    crossing_direction = 'out'
                    line_type = 'exit'
                
                # Mark vehicle as counted
                self.crossed_vehicles.add(track_id)
                
                # Update counts
                if crossing_direction == 'in':
                    self.vehicle_counts['total_in'] += 1
                else:
                    self.vehicle_counts['total_out'] += 1
                
                # Update counts by vehicle type
                if vehicle_type not in self.vehicle_counts['by_type']:
                    self.vehicle_counts['by_type'][vehicle_type] = {'in': 0, 'out': 0}
                
                if crossing_direction == 'in':
                    self.vehicle_counts['by_type'][vehicle_type]['in'] += 1
                else:
                    self.vehicle_counts['by_type'][vehicle_type]['out'] += 1
                
                # Log the crossing
                self._log_crossing(track_id, vehicle_type, crossing_direction, line_type)
                
                return True, crossing_direction, line_type
        
        return False, None, None
    
    def _check_line_crossing(self, point, direction, line_start, line_end):
        """
        Check if a point with given direction is crossing a line
        
        Args:
            point: Current point (x, y)
            direction: Direction vector (dx, dy)
            line_start: Start of line (x, y)
            line_end: End of line (x, y)
            
        Returns:
            Tuple of (is_crossing, direction)
        """
        # Calculate which side of the line the point is on
        def point_side_of_line(p, line_start, line_end):
            return ((line_end[0] - line_start[0]) * (p[1] - line_start[1]) - 
                   (line_end[1] - line_start[1]) * (p[0] - line_start[0]))
        
        # Check if point is near the line
        distance_to_line = self._point_to_line_distance(point, line_start, line_end)
        if distance_to_line > self.line_threshold:  # Threshold for line crossing
            return False, None
        
        # Check direction of movement relative to line
        line_vec = np.array(line_end) - np.array(line_start)
        line_length = np.linalg.norm(line_vec)
        if line_length == 0:
            return False, None
        
        line_normal = np.array([-line_vec[1], line_vec[0]]) / line_length
        
        # Project direction onto line normal
        direction_magnitude = np.linalg.norm(direction)
        if direction_magnitude == 0:
            return False, None
        
        direction_normalized = np.array(direction) / direction_magnitude
        dot_product = np.dot(direction_normalized, line_normal)
        
        # Determine crossing direction
        if dot_product > self.direction_threshold:  # Threshold for direction detection
            return True, 'in'
        elif dot_product < -self.direction_threshold:
            return True, 'out'
        
        return False, None
    
    def _point_to_line_distance(self, point, line_start, line_end):
        """
        Calculate distance from point to line
        
        Args:
            point: Point (x, y)
            line_start: Line start (x, y)
            line_end: Line end (x, y)
            
        Returns:
            Distance from point to line
        """
        A = line_end[1] - line_start[1]
        B = line_start[0] - line_end[0]
        C = line_end[0] * line_start[1] - line_start[0] * line_end[1]
        
        distance = abs(A * point[0] + B * point[1] + C) / np.sqrt(A**2 + B**2)
        return distance
    
    def _log_crossing(self, track_id, vehicle_type, direction, line_type):
        """
        Log a vehicle crossing event
        
        Args:
            track_id: ID of the vehicle
            vehicle_type: Type of vehicle
            direction: 'in' or 'out'
            line_type: 'entry' or 'exit'
        """
        timestamp = datetime.now()
        log_entry = {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'track_id': track_id,
            'vehicle_type': vehicle_type,
            'direction': direction,
            'line_type': line_type
        }
        
        if direction == 'in':
            self.entry_log.append(log_entry)
        else:
            self.exit_log.append(log_entry)
    
    def draw_roi(self, frame):
        """
        Draw the ROI polygon and counting lines on frame
        
        Args:
            frame: Input frame
            
        Returns:
            Frame with ROI drawn
        """
        frame_copy = frame.copy()
        
        # Draw ROI polygon
        if self.roi_polygon is not None:
            # Convert to integer coordinates
            roi_polygon_int = np.array(self.roi_polygon, dtype=np.int32)
            cv2.polylines(frame_copy, [roi_polygon_int], True, (0, 255, 255), 2)
            
            # Draw ROI points
            for point in self.roi_points:
                cv2.circle(frame_copy, (int(point[0]), int(point[1])), 5, (0, 255, 255), -1)
        
        # Draw counting lines
        for line in self.counting_lines:
            color = (0, 255, 0) if line['type'] == 'entry' else (0, 0, 255)
            cv2.line(frame_copy, 
                    (int(line['start'][0]), int(line['start'][1])), 
                    (int(line['end'][0]), int(line['end'][1])), 
                    color, 2)
            
            # Add labels
            mid_point = (int((line['start'][0] + line['end'][0]) // 2),
                        int((line['start'][1] + line['end'][1]) // 2))
            cv2.putText(frame_copy, line['type'].upper(), 
                       mid_point, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return frame_copy
    
    def draw_counts(self, frame):
        """
        Draw vehicle counts on frame
        
        Args:
            frame: Input frame
            
        Returns:
            Frame with counts drawn
        """
        frame_copy = frame.copy()
        
        # Display total counts
        cv2.putText(frame_copy, f"IN: {self.vehicle_counts['total_in']}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame_copy, f"OUT: {self.vehicle_counts['total_out']}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        # Display counts by type
        y_offset = 90
        for vehicle_type, counts in self.vehicle_counts['by_type'].items():
            cv2.putText(frame_copy, f"{vehicle_type.upper()} IN: {counts['in']}", (10, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            y_offset += 25
            cv2.putText(frame_copy, f"{vehicle_type.upper()} OUT: {counts['out']}", (10, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
            y_offset += 35
        
        return frame_copy
    
    def get_counts(self):
        """
        Get current vehicle counts
        
        Returns:
            Dictionary of current counts
        """
        return self.vehicle_counts
    
    def get_logs(self):
        """
        Get vehicle crossing logs
        
        Returns:
            Tuple of (entry_log, exit_log)
        """
        return self.entry_log, self.exit_log
    
    def reset_counts(self):
        """
        Reset all vehicle counts and logs
        """
        self.vehicle_counts = {
            'total_in': 0,
            'total_out': 0,
            'by_type': {}
        }
        self.crossed_vehicles = set()
        self.entry_log = []
        self.exit_log = []
