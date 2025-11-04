import requests, time, argparse, random
from results_logger import log_error

SERVER_URL = "http://127.0.0.1:5000/api/vehicle"
DEFAULT_VEHICLE_ID = "AMB001"

# Demo route approaching the intersection near (12.9716, 77.5945)
# Updated to approach from SOUTH to NORTH along same longitude for NS axis
route = [
    (12.9698, 77.5945, 38),
    (12.9704, 77.5945, 40),
    (12.9710, 77.5945, 42),
    (12.9713, 77.5945, 44),
    (12.9715, 77.5945, 40),  
    (12.9717, 77.5945, 35),
]

def send_point(vehicle_id: str, lat: float, lon: float, speed: float):
    payload = {"id": vehicle_id, "lat": lat, "lon": lon, "speed": speed}
    try:
        r = requests.post(SERVER_URL, json=payload, timeout=5)
        print("Sent:", payload, "| Server:", r.json())
    except Exception as e:
        print("Error sending:", e)
        log_error(str(e), "VEHICLE_SIMULATOR_COMMUNICATION")

def run_route_once(vehicle_id: str, interval: float, jitter: float):
    for i, (lat, lon, speed) in enumerate(route, 1):
        print(f"{vehicle_id} point {i}/{len(route)}: {lat:.6f}, {lon:.6f} @ {speed} km/h")
        send_point(vehicle_id, lat, lon, speed)
        sleep_s = max(0.1, interval + random.uniform(-jitter, jitter))
        time.sleep(sleep_s)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vehicle simulator")
    parser.add_argument("--id", dest="vehicle_id", default=DEFAULT_VEHICLE_ID, help="Vehicle ID (default AMB001)")
    parser.add_argument("--repeat", action="store_true", help="Repeat the route forever")
    parser.add_argument("--interval", type=float, default=3.0, help="Seconds between points (default 3.0)")
    parser.add_argument("--jitter", type=float, default=0.4, help="Random jitter added/subtracted to interval (default 0.4)")
    args = parser.parse_args()

    print("Vehicle simulator starting...")
    if args.repeat:
        print("Repeating route. Press Ctrl+C to stop.")
        try:
            while True:
                run_route_once(args.vehicle_id, args.interval, args.jitter)
        except KeyboardInterrupt:
            print("Stopped.")
    else:
        print("Sending GPS points to server...")
        run_route_once(args.vehicle_id, args.interval, args.jitter)
        print("Route complete. Check results/ folder for detailed logs.")