# Intersection coordinates (example: Bengaluru)
INTERSECTION = {"lat": 12.9716, "lon": 77.5945}

# Distance threshold (meters) to trigger priority
THRESHOLD_METERS = 200

# Optional: hold priority until the vehicle passes the intersection
# Default remains duration-based priority if set to False
HOLD_UNTIL_PASS = False

# When HOLD_UNTIL_PASS=True, release after vehicle moves beyond this distance
# Use a small hysteresis above THRESHOLD_METERS to avoid flapping
RELEASE_THRESHOLD_METERS = 240

# Traffic controller API endpoint
TRAFFIC_CONTROLLER_URL = "http://127.0.0.1:5001/api/priority"
TRAFFIC_CONTROLLER_HOLD_URL = "http://127.0.0.1:5001/api/priority_hold"
TRAFFIC_CONTROLLER_RELEASE_URL = "http://127.0.0.1:5001/api/priority_release"

# How long the intersection should grant priority (seconds)
DEFAULT_PRIORITY_SECONDS = 10