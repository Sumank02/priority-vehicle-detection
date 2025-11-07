# Priority Vehicle Detection & Display (Software-Only Demo)

This project simulates an emergency vehicle sending GPS data to a central server,
which then triggers an intersection controller to give priority (green light).

Components:
- **vehicle/**: Vehicle GPS sender (simulator + Pi GSM+GPS client scaffold)
  - `vehicle_sim.py` – Ambulance (`AMB001`)
  - `firetruck_sim.py` – Firetruck (`FIRT001`)
- **server/**: Central Flask server (distance check + priority trigger)
- **traffic_controller/**: Intersection signal simulator (with future GPIO hooks)
- **dashboard/**: Live webpage that shows the current state
- **tests/**: Basic tests for endpoints
- **results_logger.py**: Saves results to text/CSV so you can review later

## Quick Start

1) Create a local Python environment
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
```

2) Install required packages
```bash
pip install -r requirements.txt
```

3) Easiest way to run everything (Windows PowerShell)
```bash
powershell -ExecutionPolicy Bypass -File .\run_all.ps1
```
This single command starts the Traffic Controller, Server, Dashboard, and both simulators (Ambulance + Firetruck), then opens the dashboard at `http://127.0.0.1:5100`.

If you prefer starting manually, use the next section.

## Running the System (manual tabs)
Open 4 terminal tabs (or windows), and run one in each:

```bash
# Traffic controller (port 5001)
python -m traffic_controller.traffic_controller

# Server (port 5000)
python -m server.server

# Dashboard (port 5100)
python -m dashboard.app

# Ambulance simulator (AMB001)
python -m vehicle.vehicle_sim --repeat --interval 3 --jitter 0.5

# Firetruck simulator (FIRT001) — run in another tab if you want both
python -m vehicle.firetruck_sim --repeat --interval 2.5 --jitter 0.4
```

## Results Logging

The system automatically logs all events to timestamped files in the `results/` folder:
- **Text logs**: Detailed human-readable logs with timestamps
- **CSV data**: Structured data for analysis in Excel/Google Sheets
- **Session tracking**: Each run creates a new session with unique timestamp

### View Results

```bash
python view_results.py
```

### What Gets Logged
- Vehicle detection events (GPS coordinates, speed, distance)
- Priority triggers (when and which direction)
- Traffic controller state changes
- Errors and communication failures
- Session summaries with event counts

### Results Files
- `results_YYYYMMDD_HHMMSS.txt` - Human-readable logs
- `results_YYYYMMDD_HHMMSS.csv` - Excel-compatible data
- Files are created automatically when you start the system

---

## Blynk Mobile App Alerts (SOS-Style Full-Screen Alerts)

The system sends **SOS-style full-screen alerts** to your Blynk mobile app with:
- **Full-screen black background** with large white text (like emergency alerts)
- **Structured data display**: Vehicle name, ID, direction, and distance
- **Buzzer sounds** - automatic beep alerts
- **LED/Blinker effects** - flashing visual indicators
- **Color-coded themes** - Blue for Ambulance, Red for Firetruck

### Quick Setup

1. **Get Your Blynk Auth Token**
   - Go to https://blynk.cloud/
   - Create/login to your account
   - Create a new template or device
   - Copy your Auth Token
   - Update `server/config.py` with your token:
     ```python
     BLYNK_AUTH_TOKEN = "YOUR_TOKEN_HERE"
     ```

2. **Follow the Detailed Setup Guide**
   
   **📖 See [BLYNK_SETUP_GUIDE.md](BLYNK_SETUP_GUIDE.md) for complete step-by-step instructions:**
   - Which widgets to add (Label, Buzzer, LED, etc.)
   - Exact datastream assignments (V0-V7)
   - Widget configuration settings
   - Layout arrangement for SOS-style alert
   - Font sizes, colors, and positioning
   - Troubleshooting tips

### Virtual Pin Configuration

The system uses these virtual pins (configured in `server/config.py`):

| Pin | Purpose | Widget Type |
|-----|---------|-------------|
| **V0** | Alert Status (1=active, 0=inactive) | Button/Label |
| **V1** | Vehicle Name ("Ambulance"/"Firetruck") | Label |
| **V2** | Vehicle ID ("AMB001"/"FIRT001") | Label |
| **V3** | Direction ("NS"/"EW") | Label |
| **V4** | Distance (meters, e.g., "120.5") | Label |
| **V5** | Buzzer (1=ON, 0=OFF) | Buzzer |
| **V6** | LED/Blinker (255=ON, 0=OFF) | LED |
| **V7** | Color Code (RRGGBB format) | Color Picker |

### How It Works

When a priority vehicle is detected:
1. **Alert Status (V0)** = 1 (triggers full alert display)
2. **Vehicle Name (V1)** = "Ambulance" or "Firetruck"
3. **Vehicle ID (V2)** = "AMB001" or "FIRT001"
4. **Direction (V3)** = "NS" or "EW"
5. **Distance (V4)** = distance in meters (e.g., "120.5")
6. **Buzzer (V5)** = 1 (triggers sound)
7. **LED (V6)** = 255 (triggers fast blinking)
8. **Color (V7)** = vehicle-specific color (blue/red)
9. After 10 seconds, alert automatically resets

### Alert Features

- **SOS-style display**: Black background with large white text
- **Full-screen responsive**: All text clearly visible
- **Ambulance alerts**: Blue theme (#3B82F6) with "Ambulance" text
- **Firetruck alerts**: Red theme (#EF4444) with "Firetruck" text
- **Auto-reset**: Alert turns off after 10 seconds
- **Structured data**: Each piece of information sent separately for better display

### For Complete Setup Instructions

**👉 Please see [BLYNK_SETUP_GUIDE.md](BLYNK_SETUP_GUIDE.md) for detailed step-by-step widget setup and configuration!**

---

## Hardware Demo (LED Intersection Modal)

If you want a physical LED intersection model driven by the controller:

- See `Modal.md` for wiring, configuration, and run steps.
- When running the controller on a Raspberry Pi and the server on another machine, update `server/config.py` to point `TRAFFIC_CONTROLLER_URL`, `TRAFFIC_CONTROLLER_HOLD_URL`, and `TRAFFIC_CONTROLLER_RELEASE_URL` to the Pi's IP (not `127.0.0.1`).
- Optional: set `HOLD_UNTIL_PASS = True` in `server/config.py` to keep a lane green until the vehicle passes; otherwise the default duration-based behavior remains.

---

## Priority Vehicle Annotation (Upload → Analyze → Annotated Output)

Run this lightweight, separate dashboard for uploading images/videos and getting annotated results (YOLO-based):

- One command (Windows PowerShell):
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\run_pv_annotation.ps1
  ```
- Manual:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\python.exe -m pip install -r .\pv_annotation\requirements.txt
  .\.venv\Scripts\python.exe .\pv_annotation\app.py
  ```
  Then open `http://127.0.0.1:5600`.

## For Everyone (Step‑by‑Step Guide)
This section is written for non‑technical users. Follow it exactly and you’ll see the live dashboard.

1) Install once
- Make sure you have Python 3.10+ installed.
- Open the project folder in your editor (or File Explorer), then open a PowerShell window in that folder.
- Run:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  ```

2) Start everything with one command (recommended)
- In PowerShell, run:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\run_all.ps1
  ```
- This will: start the Traffic Controller, the Server, the Dashboard, and both simulators (Ambulance and Firetruck), then open the dashboard in your browser.

3) If the browser doesn’t open automatically
- Manually open: `http://127.0.0.1:5100`

4) What you’ll see on the dashboard
- Two rows (panels):
  - Ambulance (AMB001)
  - FireTruck (FIRT001)
- Each panel shows:
  - Live Distance, Bearing, Signal Direction, Vehicle ID
  - The latest “Server Last Event” (what the backend calculated)
  - The “Traffic Controller State” (shared controller’s current mode/direction)
  - A Distance Trend chart for the last ~50 updates
- A top badge shows overall system state: NORMAL (most of the time), PRIORITY (briefly when a vehicle is close), or PAUSED (no new data in a while).

5) Stopping and restarting
- To stop: close the windows that launched for the controller/server/dashboard/simulators, or run:
  ```powershell
  taskkill /IM python.exe /F
  ```
- To start again: re-run the one‑liner:
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\run_all.ps1
  ```

6) Clearing old results (optional)
```powershell
if (Test-Path "results") { Remove-Item -Recurse -Force results }
```
New logs are created automatically on the next run.

## FAQs
- Why do both panels show the same controller direction?
  - There is one shared intersection controller, so its active direction is global. Each vehicle panel still shows its own Distance/Bearing/Direction (server‑computed), but the “controller state” is shared.

- Why is the status NORMAL most of the time?
  - Emergency vehicles are rare. The controller is normally in mode “normal” and temporarily switches to “priority” when an approaching vehicle is close enough.

- How can I run just one simulator?
  - Open a PowerShell tab and run one of these:
    ```powershell
    .\.venv\Scripts\python.exe -m vehicle.vehicle_sim --repeat --interval 3 --jitter 0.5
    .\.venv\Scripts\python.exe -m vehicle.firetruck_sim --repeat --interval 2.5 --jitter 0.4
    ```

- The dashboard says “Failed to fetch”
  - Start the services (controller/server/dashboard). Using the one‑liner is easiest.

- The chart stops moving
  - That panel shows PAUSED when no fresh events arrive for ~6 seconds. Start a simulator or wait for the next update.

- I want bigger fonts/higher contrast
  - You can zoom your browser (Ctrl + + / Ctrl + -) or adjust colors in `dashboard/static/styles.css`.

---

## Result Summary
- Dashboard panels:
  - **Ambulance (AMB001)** and **FireTruck (FIRT001)** each have their own live metrics, last server event JSON, traffic controller state, and a distance trend chart.
  - The top status badge shows **PRIORITY** if either vehicle is in priority mode, **NORMAL** otherwise, and **PAUSED** if no new data has arrived for a short while.
- Metrics shown per vehicle:
  - **Distance**: Current distance to the intersection (meters).
  - **Bearing**: Initial bearing from vehicle to the intersection (degrees).
  - **Signal Direction**: Axis the controller will prioritize (NS or EW).
  - **Vehicle**: Fixed ID (AMB001 or FIRT001).
- Server Last Event: Latest computed snapshot for that vehicle (timestamp, distance, bearing, direction, priority flag).
- Traffic Controller State: Current mode (normal/priority) and active direction.

### Distance Trend (per vehicle)
- **What it is**: The Distance Trend is a small line chart that shows how far the vehicle is from the intersection over recent updates. Each panel has its own trend (AMB001 and FIRT001), updated every 2 seconds when new data arrives.
- **What’s plotted**:
  - **Y-axis (left)**: Distance to the intersection in meters (m). The scale auto-adjusts to the min/max of the last 50 points to keep the curve readable.
  - **X-axis (bottom)**: Sample index over time, newest at “now” on the far right. Labels like -1, -2, … indicate how many samples ago that point was received (roughly 2s per step).
- **How it’s graphed**:
  - The chart keeps a rolling buffer of up to 50 distance values per vehicle.
  - A new point is added only when the server’s timestamp changes (i.e., a real new event), preventing flat repeats.
  - Gridlines are drawn for quick reading, and units are shown (m on Y; relative sample position on X).
  - If no new data arrives for ~6 seconds, the badge shows **PAUSED** and the trend holds until the next event.