from flask import Flask, request, jsonify
import threading, time, os
from . import gpio_control as hw
from results_logger import log_priority_trigger, log_controller_event
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # enable CORS for all routes

priority_mode = False
state = {"mode": "normal", "direction": "NS"}
hold_active = False  # when True, remain in priority until explicitly released

CYCLE_NS = 5
CYCLE_EW = 5

def normal_cycle():
    global priority_mode, state
    while True:
        if not priority_mode:
            state.update({"mode": "normal", "direction": "NS"})
            hw.set_signal(ns_green=True, ew_green=False)
            log_controller_event(state)
            time.sleep(CYCLE_NS)
            if priority_mode:  # re-check
                continue
            state.update({"mode": "normal", "direction": "EW"})
            hw.set_signal(ns_green=False, ew_green=True)
            log_controller_event(state)
            time.sleep(CYCLE_EW)
        else:
            time.sleep(0.5)

def trigger_priority(direction="NS", duration=10):
    global priority_mode, state
    priority_mode = True
    state.update({"mode": "priority", "direction": direction})
    print(f"[CTRL] PRIORITY for {direction} for {duration}s")
    
    # Log the priority trigger
    log_priority_trigger(direction, duration)
    log_controller_event(state)
    
    hw.set_signal(ns_green=(direction=="NS"), ew_green=(direction=="EW"))
    time.sleep(max(1, int(duration)))
    print("[CTRL] Priority ended; resuming normal.")
    priority_mode = False

@app.route("/api/priority", methods=["POST"])
def api_priority():
    data = request.get_json(force=True)
    direction = data.get("direction", "NS").upper()
    duration = int(data.get("duration", 10))
    threading.Thread(target=trigger_priority, args=(direction, duration), daemon=True).start()
    return jsonify({"ok": True, "mode": "priority", "direction": direction, "duration": duration})

@app.route("/api/state", methods=["GET"])
def api_state():
    return jsonify(state)

# --- Hold-until-release endpoints (optional integration) ---
@app.route("/api/priority_hold", methods=["POST"])
def api_priority_hold():
    global priority_mode, state, hold_active
    data = request.get_json(force=True)
    direction = data.get("direction", "NS").upper()
    hold_active = True
    priority_mode = True
    state.update({"mode": "priority", "direction": direction})
    print(f"[CTRL] PRIORITY HOLD engaged for {direction}")
    log_priority_trigger(direction, 0)
    log_controller_event(state)
    hw.set_signal(ns_green=(direction=="NS"), ew_green=(direction=="EW"))
    return jsonify({"ok": True, "mode": "priority", "direction": direction, "hold": True})

@app.route("/api/priority_release", methods=["POST"])
def api_priority_release():
    global priority_mode, state, hold_active
    hold_active = False
    priority_mode = False
    # state will be updated by normal cycle shortly; log transition
    print("[CTRL] PRIORITY HOLD released; resuming normal cycle")
    log_controller_event({"mode": "normal", "direction": state.get("direction", "NS")})
    return jsonify({"ok": True, "released": True, "mode": "normal"})

if __name__ == "__main__":
    try:
        threading.Thread(target=normal_cycle, daemon=True).start()
        app.run(host="0.0.0.0", port=5001)
    finally:
        hw.cleanup()