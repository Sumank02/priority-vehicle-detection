# -----------------------------------------------------------------------------
# ⚙️ Configuration File for Priority Vehicle Detection Server
# -----------------------------------------------------------------------------
# This file defines all tunable parameters for intersection behavior,
# thresholds, and third-party integrations (like Blynk IoT).
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# 🧭 Intersection Location (Latitude & Longitude)
# -----------------------------------------------------------------------------
INTERSECTION = {
    "lat": 12.9716,    # Example intersection latitude
    "lon": 77.5945,    # Example intersection longitude
}

# -----------------------------------------------------------------------------
# 🎯 Detection and Signal Logic
# -----------------------------------------------------------------------------
THRESHOLD_METERS = 120             # Distance to trigger priority (in meters)
DEFAULT_PRIORITY_SECONDS = 10      # Duration to keep signal in priority mode
HOLD_UNTIL_PASS = True             # Keep signal green until vehicle passes
RELEASE_THRESHOLD_METERS = 150     # Distance beyond which hold is released

# -----------------------------------------------------------------------------
# 🚦 Traffic Controller URLs
# -----------------------------------------------------------------------------
TRAFFIC_CONTROLLER_URL = "http://127.0.0.1:5001/api/priority"
TRAFFIC_CONTROLLER_HOLD_URL = "http://127.0.0.1:5001/api/priority_hold"
TRAFFIC_CONTROLLER_RELEASE_URL = "http://127.0.0.1:5001/api/priority_release"

# -----------------------------------------------------------------------------
# ☁️ Blynk IoT Configuration
# -----------------------------------------------------------------------------
# Add your Blynk credentials here to enable live alerts on mobile app
# Get your AUTH TOKEN from https://blynk.cloud/ → Templates → Devices
# -----------------------------------------------------------------------------
BLYNK_AUTH_TOKEN = "1r7g_Ze_fDO_gAIfpe2ZVIkjOora17o7"  # 🔑 Replace this with your token
BLYNK_BASE_URL = "https://blynk.cloud/external/api"  # Blynk Cloud API

# SOS Alert Virtual Pins - Structured data for full-screen alert
BLYNK_VPIN_ALERT_STATUS = "V0"   # Alert status (1=active, 0=inactive) - triggers full alert display
BLYNK_VPIN_VEHICLE_NAME = "V1"   # Vehicle name (e.g., "Ambulance" or "Firetruck")
BLYNK_VPIN_VEHICLE_ID = "V2"     # Vehicle ID (e.g., "AMB001" or "FIRT001")
BLYNK_VPIN_DIRECTION = "V3"      # Direction (e.g., "NS" or "EW")
BLYNK_VPIN_DISTANCE = "V4"       # Distance in meters (e.g., "120.5")
BLYNK_VPIN_BUZZER = "V5"         # Buzzer widget (sound alerts) - value 1=ON, 0=OFF
BLYNK_VPIN_LED = "V6"            # LED/Blinker widget (visual flashing) - value 255=ON, 0=OFF
BLYNK_VPIN_COLOR = "V7"          # Color code (RRGGBB format, e.g., "3B82F6" for blue)