from flask import Flask, request, jsonify
import requests, time
from . import config
from .utils import haversine, initial_bearing, direction_from_bearing
from results_logger import log_vehicle_event, log_error
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # enable CORS for all routes

# Keep a global summary and also per-vehicle latest event
last_event = {
    "ts": None,
    "vehicle": None,
    "distance_m": None,
    "direction": None,
    "priority_triggered": False,
}
last_events_by_vehicle = {}  # vid -> last_event_like_dict

@app.route("/api/vehicle", methods=["POST"])
def vehicle():
    data = request.get_json(force=True)
    vid = data.get("id", "UNKNOWN")
    lat, lon = float(data["lat"]), float(data["lon"])
    speed = float(data.get("speed", 0))

    dist = haversine(lat, lon, config.INTERSECTION["lat"], config.INTERSECTION["lon"])
    bearing = initial_bearing(lat, lon, config.INTERSECTION["lat"], config.INTERSECTION["lon"])
    axis = direction_from_bearing(bearing)

    print(f"[SERVER] {vid} @ {lat:.6f},{lon:.6f} speed={speed:.1f} -> {dist:.1f} m | bearing={bearing:.1f}° => {axis}")

    triggered = False
    if dist < config.THRESHOLD_METERS:
        triggered = True
        try:
            if getattr(config, "HOLD_UNTIL_PASS", False):
                # Engage hold mode
                r = requests.post(
                    getattr(config, "TRAFFIC_CONTROLLER_HOLD_URL", config.TRAFFIC_CONTROLLER_URL),
                    json={"direction": axis},
                    timeout=5,
                )
            else:
                r = requests.post(
                    config.TRAFFIC_CONTROLLER_URL,
                    json={"direction": axis, "duration": config.DEFAULT_PRIORITY_SECONDS},
                    timeout=5,
                )
            print("[SERVER] priority -> controller:", r.status_code, r.text)
        except Exception as e:
            print("[SERVER] ERROR contacting controller:", e)
            log_error(str(e), "SERVER_CONTROLLER_COMMUNICATION")
    elif getattr(config, "HOLD_UNTIL_PASS", False) and dist > getattr(config, "RELEASE_THRESHOLD_METERS", config.THRESHOLD_METERS + 40):
        # If hold mode is active upstream, release when beyond hysteresis threshold
        try:
            r = requests.post(
                getattr(config, "TRAFFIC_CONTROLLER_RELEASE_URL", config.TRAFFIC_CONTROLLER_URL),
                json={},
                timeout=5,
            )
            print("[SERVER] release -> controller:", r.status_code, r.text)
        except Exception as e:
            print("[SERVER] ERROR contacting controller (release):", e)
            log_error(str(e), "SERVER_CONTROLLER_COMMUNICATION_RELEASE")

    # Update last event (overall)
    last_event.update({
        "ts": time.time(),
        "vehicle": vid,
        "distance_m": dist,
        "bearing": bearing,
        "direction": axis,
        "priority_triggered": triggered,
        "status": "priority_triggered" if triggered else "normal"
    })

    # Update per-vehicle
    last_events_by_vehicle[vid] = dict(last_event)

    # Log the vehicle event
    log_vehicle_event(last_event, data)

    return jsonify({
        "status": "priority_triggered" if triggered else "normal",
        "distance_m": dist,
        "direction": axis
    })

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)