#!/usr/bin/env python3
"""
Results Viewer for Priority Vehicle Detection
Run this script to see the latest results and summary
"""

import os
import glob
from results_logger import get_summary

def list_results_files():
    """List all available results files"""
    results_dir = "results"
    if not os.path.exists(results_dir):
        print("No results directory found. Run the system first to generate results.")
        return []
    
    txt_files = glob.glob(os.path.join(results_dir, "results_*.txt"))
    csv_files = glob.glob(os.path.join(results_dir, "results_*.csv"))
    
    return txt_files, csv_files

def show_latest_results():
    """Show the latest results summary"""
    txt_files, csv_files = list_results_files()
    
    if not txt_files:
        print("No results files found. Run the system first!")
        return
    
    # Get the most recent text file
    latest_txt = max(txt_files, key=os.path.getctime)
    latest_csv = max(csv_files, key=os.path.getctime) if csv_files else None
    
    print(f"📊 LATEST RESULTS")
    print(f"Text log: {latest_txt}")
    if latest_csv:
        print(f"CSV data: {latest_csv}")
    print("="*60)
    
    # Show summary
    try:
        summary = get_summary()
        print(summary)
    except Exception as e:
        print(f"Error getting summary: {e}")
    
    # Show last few lines of the log
    try:
        with open(latest_txt, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print("\n📝 LAST 10 LOG ENTRIES:")
            print("-" * 40)
            for line in lines[-10:]:
                line = line.strip()
                if line and not line.startswith('='):
                    print(line)
    except Exception as e:
        print(f"Error reading log file: {e}")

def show_all_sessions():
    """Show all available sessions"""
    txt_files, csv_files = list_results_files()
    
    if not txt_files:
        print("No results files found.")
        return
    
    print("📁 ALL AVAILABLE SESSIONS:")
    print("=" * 60)
    
    for txt_file in sorted(txt_files, key=os.path.getctime, reverse=True):
        filename = os.path.basename(txt_file)
        timestamp = filename.replace("results_", "").replace(".txt", "")
        size = os.path.getsize(txt_file)
        
        print(f"📄 {filename}")
        print(f"   Timestamp: {timestamp}")
        print(f"   Size: {size} bytes")
        print()

def main():
    print("🚗 PRIORITY VEHICLE DETECTION - RESULTS VIEWER")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("1. Show latest results")
        print("2. List all sessions")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            show_latest_results()
        elif choice == "2":
            show_all_sessions()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main() 