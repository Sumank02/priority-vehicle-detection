# -----------------------------------------------------------------------------
# 🚦 Priority Vehicle Detection Server
# -----------------------------------------------------------------------------
# This is the main logic of the system. It:
# - Receives live GPS data from vehicles
# - Calculates distance and direction
# - Sends control commands to the traffic controller
# - Sends alert messages to the Blynk IoT app
# -----------------------------------------------------------------------------

from flask import Flask, request, jsonify
import requests, time
from urllib.parse import quote
from . import config
from .utils import haversine, initial_bearing, direction_from_bearing
from results_logger import log_vehicle_event, log_error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# -----------------------------------------------------------------------------
# 🔢 Global variables to keep the latest state
# -----------------------------------------------------------------------------
last_event = {
    "ts": None,
    "vehicle": None,
    "distance_m": None,
    "direction": None,
    "priority_triggered": False,
}
last_events_by_vehicle = {}
# Track which vehicles currently have active alerts (to avoid spamming)
active_alerts = {}  # {vehicle_id: True/False}

# -----------------------------------------------------------------------------
# 🔔 Function: send_blynk_alert()
# -----------------------------------------------------------------------------
# Sends SOS-style alert to Blynk Cloud with structured data:
# - Full-screen alert display with separate data streams
# - Vehicle name, ID, direction, and distance
# - Buzzer activation (sound alert)
# - LED/Blinker activation (visual flashing)
# - Color indicators based on vehicle type
# -----------------------------------------------------------------------------
def send_blynk_alert(vehicle_id, distance, direction=None):
    try:
        # Identify vehicle type
        is_ambulance = "AMB" in vehicle_id.upper()
        name = "Ambulance" if is_ambulance else "Firetruck"
        
        # Choose colors based on vehicle type
        if is_ambulance:
            color_code = "3B82F6"  # Blue (hex without #)
            color_rgb = "59,130,246"  # RGB for reference
        else:
            color_code = "EF4444"  # Red (hex without #)
            color_rgb = "239,68,68"  # RGB for reference
        
        # Get direction from global state if not provided
        if direction is None:
            direction = last_event.get("direction", "NS")
        
        # Construct base API parameters
        base_params = f"token={config.BLYNK_AUTH_TOKEN}"
        
        # Build URLs for all data streams
        urls = [
            # V0: Alert Status (1 = active, triggers full alert display)
            (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_ALERT_STATUS}=1", "Alert Status"),
            
            # V1: Vehicle Name (e.g., "Ambulance" or "Firetruck")
            (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_VEHICLE_NAME}={quote(name)}", "Vehicle Name"),
            
            # V2: Vehicle ID (e.g., "AMB001" or "FIRT001")
            (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_VEHICLE_ID}={quote(vehicle_id)}", "Vehicle ID"),
            
            # V3: Direction (e.g., "NS" or "EW")
            (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_DIRECTION}={quote(direction)}", "Direction"),
            
            # V4: Distance (e.g., "120.5")
            (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_DISTANCE}={distance:.1f}", "Distance"),
            
            # V5: Buzzer (1 = ON, triggers sound)
            (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_BUZZER}=1", "Buzzer"),
            
            # V6: LED/Blinker (255 = ON, triggers flashing)
            (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_LED}=255", "LED/Blinker"),
            
            # V7: Color Code (RRGGBB format)
            (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_COLOR}={color_code}", "Color Code"),
        ]
        
        # Send all data streams in parallel
        responses = []
        for url, widget_name in urls:
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    responses.append(f"✓ {widget_name}")
                else:
                    responses.append(f"✗ {widget_name}: {r.text[:50]}")
            except Exception as e:
                responses.append(f"✗ {widget_name}: {str(e)[:50]}")
        
        print(f"[BLYNK] SOS Alert sent → {name} ({vehicle_id}) | Direction: {direction} | Distance: {distance:.1f}m | {', '.join(responses)}")
        
        # Mark this vehicle as having an active alert
        active_alerts[vehicle_id] = True
        
    except Exception as e:
        print("[BLYNK] Error sending alert:", e)
        log_error(str(e), "BLYNK_ALERT_ERROR")


# -----------------------------------------------------------------------------
# 🔕 Function: turn_off_blynk_alert()
# -----------------------------------------------------------------------------
# Turns off V0, V5, and V6 when priority ends (vehicle moves out of range)
# -----------------------------------------------------------------------------
def turn_off_blynk_alert(vehicle_id=None):
    try:
        base_params = f"token={config.BLYNK_AUTH_TOKEN}"
        
        # Turn off V0 (Alert Status), V5 (Buzzer), and V6 (LED)
        urls = [
            (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_ALERT_STATUS}=0", "Alert Status OFF"),
            (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_BUZZER}=0", "Buzzer OFF"),
            (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_LED}=0", "LED/Blinker OFF"),
        ]
        
        responses = []
        for url, widget_name in urls:
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    responses.append(f"✓ {widget_name}")
                else:
                    responses.append(f"✗ {widget_name}: {r.text[:50]}")
            except Exception as e:
                responses.append(f"✗ {widget_name}: {str(e)[:50]}")
        
        if vehicle_id:
            active_alerts[vehicle_id] = False
            print(f"[BLYNK] Alert turned OFF → Vehicle: {vehicle_id} | {', '.join(responses)}")
        else:
            print(f"[BLYNK] Alert turned OFF → {', '.join(responses)}")
        
    except Exception as e:
        print("[BLYNK] Error turning off alert:", e)
        log_error(str(e), "BLYNK_ALERT_OFF_ERROR")


# -----------------------------------------------------------------------------
# 🚗 Endpoint: /api/vehicle [POST]
# -----------------------------------------------------------------------------
# This endpoint receives GPS data from the vehicle and decides whether
# to trigger the priority signal and/or send Blynk alerts.
# -----------------------------------------------------------------------------
@app.route("/api/vehicle", methods=["POST"])
def vehicle():
    data = request.get_json(force=True)
    vid = data.get("id", "UNKNOWN")
    lat, lon = float(data["lat"]), float(data["lon"])
    speed = float(data.get("speed", 0))

    # Calculate distance and direction
    dist = haversine(lat, lon, config.INTERSECTION["lat"], config.INTERSECTION["lon"])
    bearing = initial_bearing(lat, lon, config.INTERSECTION["lat"], config.INTERSECTION["lon"])
    axis = direction_from_bearing(bearing)

    print(f"[SERVER] {vid} @ {lat:.6f},{lon:.6f} speed={speed:.1f} → {dist:.1f} m | bearing={bearing:.1f}° → {axis}")

    triggered = False

    # -----------------------------------------------------------------------------
    # 🚨 If vehicle is close enough — trigger priority and send Blynk alert
    # -----------------------------------------------------------------------------
    if dist < config.THRESHOLD_METERS:
        triggered = True
        
        # Only send alert if this vehicle doesn't already have an active alert
        # This prevents spamming the same alert repeatedly
        if not active_alerts.get(vid, False):
            send_blynk_alert(vid, dist, axis)  # <-- Send SOS alert to Blynk App with direction
        else:
            # Update distance and other info while alert is active
            # Keep V0, V5, V6 ON (they stay on from initial trigger)
            # Update V1-V4, V7 with latest data
            try:
                is_ambulance = "AMB" in vid.upper()
                name = "Ambulance" if is_ambulance else "Firetruck"
                color_code = "3B82F6" if is_ambulance else "EF4444"
                
                base_params = f"token={config.BLYNK_AUTH_TOKEN}"
                update_urls = [
                    (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_VEHICLE_NAME}={quote(name)}", "Vehicle Name"),
                    (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_VEHICLE_ID}={quote(vid)}", "Vehicle ID"),
                    (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_DIRECTION}={quote(axis)}", "Direction"),
                    (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_DISTANCE}={dist:.1f}", "Distance"),
                    (f"{config.BLYNK_BASE_URL}/update?{base_params}&{config.BLYNK_VPIN_COLOR}={color_code}", "Color Code"),
                ]
                
                for url, _ in update_urls:
                    try:
                        requests.get(url, timeout=2)
                    except:
                        pass
            except:
                pass

        try:
            if getattr(config, "HOLD_UNTIL_PASS", False):
                # Engage "hold until release" mode
                r = requests.post(
                    getattr(config, "TRAFFIC_CONTROLLER_HOLD_URL", config.TRAFFIC_CONTROLLER_URL),
                    json={"direction": axis},
                    timeout=5,
                )
            else:
                # Engage timed priority mode
                r = requests.post(
                    config.TRAFFIC_CONTROLLER_URL,
                    json={"direction": axis, "duration": config.DEFAULT_PRIORITY_SECONDS},
                    timeout=5,
                )
            print("[SERVER] priority → controller:", r.status_code, r.text)
        except Exception as e:
            print("[SERVER] ERROR contacting controller:", e)
            log_error(str(e), "SERVER_CONTROLLER_COMMUNICATION")

    # -----------------------------------------------------------------------------
    # 🕓 If vehicle has passed the intersection — release hold mode and turn off alerts
    # -----------------------------------------------------------------------------
    elif dist >= config.THRESHOLD_METERS:
        # Vehicle is no longer in priority range - turn off alerts
        if active_alerts.get(vid, False):
            turn_off_blynk_alert(vid)  # Turn off V0, V5, V6
        
        if getattr(config, "HOLD_UNTIL_PASS", False) and dist > getattr(config, "RELEASE_THRESHOLD_METERS", config.THRESHOLD_METERS + 40):
            try:
                r = requests.post(
                    getattr(config, "TRAFFIC_CONTROLLER_RELEASE_URL", config.TRAFFIC_CONTROLLER_URL),
                    json={},
                    timeout=5,
                )
                print("[SERVER] release → controller:", r.status_code, r.text)
            except Exception as e:
                print("[SERVER] ERROR contacting controller (release):", e)
                log_error(str(e), "SERVER_CONTROLLER_COMMUNICATION_RELEASE")

    # -----------------------------------------------------------------------------
    # 💾 Update logs and global state
    # -----------------------------------------------------------------------------
    last_event.update({
        "ts": time.time(),
        "vehicle": vid,
        "distance_m": dist,
        "bearing": bearing,
        "direction": axis,
        "priority_triggered": triggered,
        "status": "priority_triggered" if triggered else "normal"
    })

    last_events_by_vehicle[vid] = dict(last_event)
    log_vehicle_event(last_event, data)

    # -----------------------------------------------------------------------------
    # 📤 Respond to vehicle
    # -----------------------------------------------------------------------------
    return jsonify({
        "status": "priority_triggered" if triggered else "normal",
        "distance_m": dist,
        "direction": axis
    })


# -----------------------------------------------------------------------------
# 📋 Endpoint: /api/last_event [GET]
# -----------------------------------------------------------------------------
# Returns latest global or per-vehicle event info.
# -----------------------------------------------------------------------------
@app.route("/api/last_event", methods=["GET"])
def api_last_event():
    vid = request.args.get("id")
    if vid:
        return jsonify(last_events_by_vehicle.get(vid, {
            "ts": None,
            "vehicle": vid,
            "distance_m": None,
            "bearing": None,
            "direction": None,
            "priority_triggered": False,
            "status": "unknown"
        }))
    return jsonify(last_event)


# -----------------------------------------------------------------------------
# ▶️ Run Flask Server
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)