import time, random, argparse
import requests
from typing import Tuple
from results_logger import log_error

SERVER_URL = "http://127.0.0.1:5000/api/vehicle"

# Intersection (keep in sync with server.config)
INTERSECTION = (12.9716, 77.5945)

# Two approach vectors so it doesn't feel static
# Ambulance: approach along NS (south -> intersection)
AMB_START = (12.9698, 77.5945)
# Firetruck: approach along EW (east -> intersection)
FIR_START = (12.9716, 77.5960)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def send_point(vehicle_id: str, lat: float, lon: float, speed_kmh: float):
    payload = {"id": vehicle_id, "lat": lat, "lon": lon, "speed": speed_kmh}
    try:
        r = requests.post(SERVER_URL, json=payload, timeout=5)
        print("Sent:", payload, "| Server:", r.json())
    except Exception as e:
        print("Error sending:", e)
        log_error(str(e), "SCENARIO_SIMULATOR_COMMUNICATION")


def run_instance(vehicle_id: str, start: Tuple[float, float], end: Tuple[float, float], duration_s: int, tick_s: float):
    """Simulate an approach from start -> end across duration_s seconds.
    Generates ~duration_s / tick_s points, then a couple of points beyond to simulate crossing.
    """
    steps = max(1, int(duration_s / tick_s))
    for i in range(steps + 1):
        t = i / steps
        lat = lerp(start[0], end[0], t)
        lon = lerp(start[1], end[1], t)
        # Rough speed profile: faster in middle, slower at start/end
        speed = 30 + 20 * (1 - abs(2 * t - 1))
        send_point(vehicle_id, lat, lon, speed)
        time.sleep(tick_s + random.uniform(-0.15, 0.15))

    # Two extra points beyond the intersection to indicate crossing
    lat = lerp(start[0], end[0], 1.05)
    lon = lerp(start[1], end[1], 1.05)
    send_point(vehicle_id, lat, lon, 28)
    time.sleep(tick_s)
    lat = lerp(start[0], end[0], 1.10)
    lon = lerp(start[1], end[1], 1.10)
    send_point(vehicle_id, lat, lon, 26)


def main():
    parser = argparse.ArgumentParser(description="Scenario simulator: alternating ambulance/firetruck instances")
    parser.add_argument("--min_duration", type=int, default=10, help="Min instance duration seconds (default 10)")
    parser.add_argument("--max_duration", type=int, default=15, help="Max instance duration seconds (default 15)")
    parser.add_argument("--idle", type=int, default=5, help="Idle seconds between instances (default 5)")
    parser.add_argument("--tick", type=float, default=1.0, help="Seconds between points within an instance (default 1.0)")
    args = parser.parse_args()

    print("Scenario simulator starting... Ctrl+C to stop.")
    # Alternate instances: AMB (NS) then FIRT (EW)
    types = [
        ("AMB001", AMB_START, INTERSECTION),
        ("FIRT001", FIR_START, INTERSECTION),
    ]
    idx = 0
    try:
        while True:
            vehicle_id, start, end = types[idx % len(types)]
            duration = random.randint(args.min_duration, args.max_duration)
            print(f"Instance: {vehicle_id} for {duration}s (tick {args.tick}s) -> crossing, then idle {args.idle}s")
            run_instance(vehicle_id, start, end, duration, args.tick)
            # During idle, publish 0-distance points at the intersection (speed 0)
            idle_ticks = max(1, int(args.idle / max(0.2, args.tick)))
            for _ in range(idle_ticks):
                send_point(vehicle_id, INTERSECTION[0], INTERSECTION[1], 0.0)
                time.sleep(args.tick)
            idx += 1
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()


