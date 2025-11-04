import csv
import json
import os
from datetime import datetime
from typing import Dict, Any

class ResultsLogger:
    def __init__(self, base_dir="."):
        self.base_dir = base_dir
        self.results_dir = os.path.join(base_dir, "results")
        self.ensure_results_dir()
        
        # Create results files with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.txt_file = os.path.join(self.results_dir, f"results_{timestamp}.txt")
        self.csv_file = os.path.join(self.results_dir, f"results_{timestamp}.csv")
        
        # Initialize CSV with headers
        self.init_csv()
        
        # Log session start
        self.log_session_start()
    
    def ensure_results_dir(self):
        """Create results directory if it doesn't exist"""
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
    
    def init_csv(self):
        """Initialize CSV file with headers"""
        headers = [
            'timestamp', 'event_type', 'vehicle_id', 'latitude', 'longitude', 
            'speed', 'distance_m', 'bearing', 'direction', 'priority_triggered',
            'server_status', 'controller_mode', 'controller_direction'
        ]
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def log_session_start(self):
        """Log when a new session starts"""
        session_info = f"""
{'='*60}
PRIORITY VEHICLE DETECTION - NEW SESSION
Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Results saved to: {self.txt_file}
CSV data: {self.csv_file}
{'='*60}
"""
        self.write_to_txt(session_info)
    
    def log_vehicle_event(self, server_data: Dict[str, Any], vehicle_data: Dict[str, Any] = None):
        """Log a vehicle detection event"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract data
        event_type = "VEHICLE_DETECTION"
        vehicle_id = vehicle_data.get('id', 'UNKNOWN') if vehicle_data else 'UNKNOWN'
        lat = vehicle_data.get('lat', 0) if vehicle_data else 0
        lon = vehicle_data.get('lon', 0) if vehicle_data else 0
        speed = vehicle_data.get('speed', 0) if vehicle_data else 0
        distance = server_data.get('distance_m', 0)
        bearing = server_data.get('bearing', 0)
        direction = server_data.get('direction', 'UNKNOWN')
        priority = server_data.get('priority_triggered', False)
        status = server_data.get('status', 'unknown')
        
        # Format for text log
        text_log = f"""
[{timestamp}] {event_type}
Vehicle: {vehicle_id}
Location: {lat:.6f}, {lon:.6f}
Speed: {speed:.1f} km/h
Distance to intersection: {distance:.1f} m
Bearing: {bearing:.1f}°
Direction: {direction}
Priority Triggered: {priority}
Status: {status}
{'-'*40}
"""
        self.write_to_txt(text_log)
        
        # Write to CSV
        csv_row = [
            timestamp, event_type, vehicle_id, lat, lon, speed,
            distance, bearing, direction, priority, status, '', ''
        ]
        self.write_to_csv(csv_row)
    
    def log_controller_event(self, controller_data: Dict[str, Any]):
        """Log traffic controller state changes"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        mode = controller_data.get('mode', 'unknown')
        direction = controller_data.get('direction', 'unknown')
        
        text_log = f"""
[{timestamp}] CONTROLLER_STATE_CHANGE
Mode: {mode}
Direction: {direction}
{'-'*40}
"""
        self.write_to_txt(text_log)
        
        # Update CSV with controller info (find last row and update)
        self.update_csv_controller(mode, direction)
    
    def log_priority_trigger(self, direction: str, duration: int):
        """Log when priority is triggered"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        text_log = f"""
[{timestamp}] PRIORITY_TRIGGERED
Direction: {direction}
Duration: {duration} seconds
{'-'*40}
"""
        self.write_to_txt(text_log)
    
    def log_error(self, error_msg: str, context: str = ""):
        """Log errors"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        text_log = f"""
[{timestamp}] ERROR
Context: {context}
Error: {error_msg}
{'-'*40}
"""
        self.write_to_txt(text_log)
    
    def write_to_txt(self, content: str):
        """Write content to text file"""
        try:
            with open(self.txt_file, 'a', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Error writing to text file: {e}")
    
    def write_to_csv(self, row: list):
        """Write row to CSV file"""
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
        except Exception as e:
            print(f"Error writing to CSV: {e}")
    
    def update_csv_controller(self, mode: str, direction: str):
        """Update the last CSV row with controller info"""
        try:
            # Read all rows
            rows = []
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            if len(rows) > 1:  # More than just header
                # Update last row's controller fields
                last_row = rows[-1]
                if len(last_row) >= 12:
                    last_row[11] = mode      # controller_mode
                    last_row[12] = direction # controller_direction
                
                # Write back all rows
                with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
        except Exception as e:
            print(f"Error updating CSV: {e}")
    
    def get_summary(self) -> str:
        """Get a summary of the current session"""
        try:
            with open(self.txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count different event types
            vehicle_events = content.count('VEHICLE_DETECTION')
            priority_triggers = content.count('PRIORITY_TRIGGERED')
            errors = content.count('ERROR')
            
            summary = f"""
{'='*60}
SESSION SUMMARY
Total Vehicle Events: {vehicle_events}
Priority Triggers: {priority_triggers}
Errors: {errors}
Results File: {self.txt_file}
CSV Data: {self.csv_file}
{'='*60}
"""
            return summary
        except Exception as e:
            return f"Error reading summary: {e}"

# Global logger instance
logger = ResultsLogger()

# Convenience functions
def log_vehicle_event(server_data, vehicle_data=None):
    logger.log_vehicle_event(server_data, vehicle_data)

def log_controller_event(controller_data):
    logger.log_controller_event(controller_data)

def log_priority_trigger(direction, duration):
    logger.log_priority_trigger(direction, duration)

def log_error(error_msg, context=""):
    logger.log_error(error_msg, context)

def get_summary():
    return logger.get_summary() 