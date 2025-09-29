"""
Database configuration and models for vehicle detection system
"""

import pymysql
import sqlite3
import os
from datetime import datetime, date
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Initialize database connection"""
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connect to database (MySQL or SQLite)"""
        # Check if database credentials are provided
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        
        if db_host and db_user and db_password:
            try:
                # Try MySQL first
                self.connection = pymysql.connect(
                    host=db_host,
                    user=db_user,
                    password=db_password,
                    database=os.getenv('DB_NAME', 'vehicle_detection'),
                    port=int(os.getenv('DB_PORT', 3306)),
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor,
                    connect_timeout=10
                )
                print("✅ MySQL database connected successfully")
                self.create_tables()
            except Exception as e:
                print(f"❌ MySQL connection failed: {e}")
                print("🔄 Falling back to SQLite")
                self.connection = None
                self.setup_sqlite()
        else:
            print("ℹ️ No database credentials provided, using SQLite")
            self.connection = None
            self.setup_sqlite()
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        if not self.connection:
            return
        
        try:
            with self.connection.cursor() as cursor:
                # Vehicle crossings table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vehicle_crossings (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        timestamp DATETIME NOT NULL,
                        track_id INT NOT NULL,
                        vehicle_type VARCHAR(50) NOT NULL,
                        direction ENUM('in', 'out') NOT NULL,
                        line_type VARCHAR(20) NOT NULL,
                        confidence FLOAT,
                        bbox_x1 INT,
                        bbox_y1 INT,
                        bbox_x2 INT,
                        bbox_y2 INT,
                        center_x FLOAT,
                        center_y FLOAT,
                        speed_kmh FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_timestamp (timestamp),
                        INDEX idx_vehicle_type (vehicle_type),
                        INDEX idx_direction (direction)
                    )
                """)
                
                # Daily summary table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS daily_summary (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        date DATE NOT NULL UNIQUE,
                        total_vehicles_in INT DEFAULT 0,
                        total_vehicles_out INT DEFAULT 0,
                        cars_in INT DEFAULT 0,
                        cars_out INT DEFAULT 0,
                        trucks_in INT DEFAULT 0,
                        trucks_out INT DEFAULT 0,
                        buses_in INT DEFAULT 0,
                        buses_out INT DEFAULT 0,
                        motorcycles_in INT DEFAULT 0,
                        motorcycles_out INT DEFAULT 0,
                        peak_hour_in INT,
                        peak_hour_out INT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_date (date)
                    )
                """)
                
                # Processing sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processing_sessions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        session_id VARCHAR(255) NOT NULL UNIQUE,
                        video_filename VARCHAR(255),
                        rtsp_url VARCHAR(500),
                        roi_points JSON,
                        start_time DATETIME,
                        end_time DATETIME,
                        total_frames INT,
                        vehicles_detected INT,
                        processing_status ENUM('processing', 'completed', 'failed') DEFAULT 'processing',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_session_id (session_id),
                        INDEX idx_start_time (start_time)
                    )
                """)
                
                self.connection.commit()
                print("✅ Database tables created successfully")
                
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
    
    def insert_vehicle_crossing(self, track_id, vehicle_type, direction, line_type, 
                               confidence=None, bbox=None, center=None, speed_kmh=None):
        """Insert a vehicle crossing record"""
        if not self.connection:
            return False
        
        try:
            with self.connection.cursor() as cursor:
                sql = """
                    INSERT INTO vehicle_crossings 
                    (timestamp, track_id, vehicle_type, direction, line_type, 
                     confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2, 
                     center_x, center_y, speed_kmh)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                bbox_x1 = bbox[0] if bbox and len(bbox) >= 4 else None
                bbox_y1 = bbox[1] if bbox and len(bbox) >= 4 else None
                bbox_x2 = bbox[2] if bbox and len(bbox) >= 4 else None
                bbox_y2 = bbox[3] if bbox and len(bbox) >= 4 else None
                
                center_x = center[0] if center and len(center) >= 2 else None
                center_y = center[1] if center and len(center) >= 2 else None
                
                cursor.execute(sql, (
                    datetime.now(),
                    track_id,
                    vehicle_type,
                    direction,
                    line_type,
                    confidence,
                    bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                    center_x, center_y,
                    speed_kmh
                ))
                
                self.connection.commit()
                return True
                
        except Exception as e:
            print(f"❌ Error inserting vehicle crossing: {e}")
            return False
    
    def update_daily_summary(self, date_obj=None):
        """Update daily summary for a specific date"""
        if not self.connection:
            return False
        
        if date_obj is None:
            date_obj = date.today()
        
        try:
            with self.connection.cursor() as cursor:
                # Get summary data for the date
                cursor.execute("""
                    SELECT 
                        DATE(timestamp) as date,
                        SUM(CASE WHEN direction = 'in' THEN 1 ELSE 0 END) as total_in,
                        SUM(CASE WHEN direction = 'out' THEN 1 ELSE 0 END) as total_out,
                        SUM(CASE WHEN direction = 'in' AND vehicle_type = 'car' THEN 1 ELSE 0 END) as cars_in,
                        SUM(CASE WHEN direction = 'out' AND vehicle_type = 'car' THEN 1 ELSE 0 END) as cars_out,
                        SUM(CASE WHEN direction = 'in' AND vehicle_type = 'truck' THEN 1 ELSE 0 END) as trucks_in,
                        SUM(CASE WHEN direction = 'out' AND vehicle_type = 'truck' THEN 1 ELSE 0 END) as trucks_out,
                        SUM(CASE WHEN direction = 'in' AND vehicle_type = 'bus' THEN 1 ELSE 0 END) as buses_in,
                        SUM(CASE WHEN direction = 'out' AND vehicle_type = 'bus' THEN 1 ELSE 0 END) as buses_out,
                        SUM(CASE WHEN direction = 'in' AND vehicle_type = 'motorcycle' THEN 1 ELSE 0 END) as motorcycles_in,
                        SUM(CASE WHEN direction = 'out' AND vehicle_type = 'motorcycle' THEN 1 ELSE 0 END) as motorcycles_out
                    FROM vehicle_crossings 
                    WHERE DATE(timestamp) = %s
                    GROUP BY DATE(timestamp)
                """, (date_obj,))
                
                result = cursor.fetchone()
                
                if result:
                    # Update or insert daily summary
                    cursor.execute("""
                        INSERT INTO daily_summary 
                        (date, total_vehicles_in, total_vehicles_out, cars_in, cars_out,
                         trucks_in, trucks_out, buses_in, buses_out, motorcycles_in, motorcycles_out)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        total_vehicles_in = VALUES(total_vehicles_in),
                        total_vehicles_out = VALUES(total_vehicles_out),
                        cars_in = VALUES(cars_in),
                        cars_out = VALUES(cars_out),
                        trucks_in = VALUES(trucks_in),
                        trucks_out = VALUES(trucks_out),
                        buses_in = VALUES(buses_in),
                        buses_out = VALUES(buses_out),
                        motorcycles_in = VALUES(motorcycles_in),
                        motorcycles_out = VALUES(motorcycles_out),
                        updated_at = CURRENT_TIMESTAMP
                    """, (
                        date_obj,
                        result['total_in'] or 0,
                        result['total_out'] or 0,
                        result['cars_in'] or 0,
                        result['cars_out'] or 0,
                        result['trucks_in'] or 0,
                        result['trucks_out'] or 0,
                        result['buses_in'] or 0,
                        result['buses_out'] or 0,
                        result['motorcycles_in'] or 0,
                        result['motorcycles_out'] or 0
                    ))
                    
                    self.connection.commit()
                    print(f"✅ Daily summary updated for {date_obj}")
                    return True
                
        except Exception as e:
            print(f"❌ Error updating daily summary: {e}")
            return False
    
    def get_daily_summary(self, date_obj=None):
        """Get daily summary for a specific date"""
        if not self.connection:
            return None
        
        if date_obj is None:
            date_obj = date.today()
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM daily_summary WHERE date = %s
                """, (date_obj,))
                
                return cursor.fetchone()
                
        except Exception as e:
            print(f"❌ Error getting daily summary: {e}")
            return None
    
    def get_vehicle_crossings(self, start_date=None, end_date=None, vehicle_type=None, direction=None):
        """Get vehicle crossings with filters"""
        if not self.connection:
            return []
        
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM vehicle_crossings WHERE 1=1"
                params = []
                
                if start_date:
                    sql += " AND timestamp >= %s"
                    params.append(start_date)
                
                if end_date:
                    sql += " AND timestamp <= %s"
                    params.append(end_date)
                
                if vehicle_type:
                    sql += " AND vehicle_type = %s"
                    params.append(vehicle_type)
                
                if direction:
                    sql += " AND direction = %s"
                    params.append(direction)
                
                sql += " ORDER BY timestamp DESC"
                
                cursor.execute(sql, params)
                return cursor.fetchall()
                
        except Exception as e:
            print(f"❌ Error getting vehicle crossings: {e}")
            return []
    
    def setup_sqlite(self):
        """Setup SQLite fallback database"""
        try:
            self.connection = sqlite3.connect('vehicle_detection.db')
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            print("✅ SQLite database connected successfully")
            self.create_sqlite_tables()
        except Exception as e:
            print(f"❌ SQLite setup failed: {e}")
            self.connection = None
    
    def create_sqlite_tables(self):
        """Create SQLite tables"""
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Vehicle crossings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_crossings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    track_id INTEGER NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    direction TEXT NOT NULL CHECK (direction IN ('in', 'out')),
                    line_type TEXT NOT NULL,
                    confidence REAL,
                    bbox_x1 INTEGER,
                    bbox_y1 INTEGER,
                    bbox_x2 INTEGER,
                    bbox_y2 INTEGER,
                    center_x REAL,
                    center_y REAL,
                    speed_kmh REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Daily summary table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL UNIQUE,
                    total_vehicles_in INTEGER DEFAULT 0,
                    total_vehicles_out INTEGER DEFAULT 0,
                    cars_in INTEGER DEFAULT 0,
                    cars_out INTEGER DEFAULT 0,
                    trucks_in INTEGER DEFAULT 0,
                    trucks_out INTEGER DEFAULT 0,
                    buses_in INTEGER DEFAULT 0,
                    buses_out INTEGER DEFAULT 0,
                    motorcycles_in INTEGER DEFAULT 0,
                    motorcycles_out INTEGER DEFAULT 0,
                    peak_hour_in INTEGER,
                    peak_hour_out INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Processing sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL UNIQUE,
                    video_filename TEXT,
                    rtsp_url TEXT,
                    roi_points TEXT,
                    start_time DATETIME,
                    end_time DATETIME,
                    total_frames INTEGER,
                    vehicles_detected INTEGER,
                    processing_status TEXT DEFAULT 'processing' CHECK (processing_status IN ('processing', 'completed', 'failed')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            print("✅ SQLite tables created successfully")
            
        except Exception as e:
            print(f"❌ Error creating SQLite tables: {e}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")

# Global database instance
db_manager = DatabaseManager()
