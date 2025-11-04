"""
Raspberry Pi vehicle client for GSM+GPS modules.
- SIMULATE=True will emit a demo route without using serial.
- Set SIMULATE=False and configure SERIAL_PORT for real module.
"""

import time, requests, os

# ==== CONFIG ====
SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:5000/api/vehicle")
VEHICLE_ID = os.getenv("VEHICLE_ID", "AMB001")
SIMULATE = os.getenv("SIMULATE", "true").lower() == "true"

SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyUSB2")
BAUD_RATE = int(os.getenv("BAUD_RATE", "115200"))

def send_to_server(lat, lon, speed):
    payload = {"id": VEHICLE_ID, "lat": lat, "lon": lon, "speed": speed}
    try:
        r = requests.post(SERVER_URL, json=payload, timeout=5)
        print("POST", payload, "->", r.status_code, r.text)
    except Exception as e:
        print("Error POST:", e)

def run_simulated():
    route = [
        (12.9711, 77.5940, 40),
        (12.9713, 77.5942, 44),
        (12.9715, 77.5944, 46),
        (12.9716, 77.5945, 41),
        (12.9717, 77.5946, 36),
    ]
    while True:
        for lat, lon, speed in route:
            send_to_server(lat, lon, speed)
            time.sleep(3)

def parse_cgnsinf(resp: str):
    # +CGNSINF: 1,1,UTC,lat,lon,alt,speed,...
    if "+CGNSINF" not in resp:
        return None
    parts = resp.strip().split(",")
    if len(parts) < 7:
        return None
    fix_ok = parts[1] == "1"
    if not fix_ok:
        return None
    lat = float(parts[3]); lon = float(parts[4]); speed = float(parts[6])
    return lat, lon, speed

def run_hardware():
    import serial
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    def at(cmd, delay=0.3):
        ser.write((cmd + "\r\n").encode())
        time.sleep(delay)
        return ser.read_all().decode(errors="ignore")

    # power on GNSS
    at("AT"); at("AT+CPIN?"); at("AT+CGNSPWR=1"); at("AT+CGNSSEQ=RMC")
    print("Waiting for GPS fix...")
    while True:
        resp = at("AT+CGNSINF", 0.8)
        parsed = parse_cgnsinf(resp)
        if parsed:
            lat, lon, speed = parsed
            print(f"GPS: {lat},{lon} speed={speed}")
            send_to_server(lat, lon, speed)
        else:
            print("No fix yet...")
        time.sleep(3)

if __name__ == "__main__":
    if SIMULATE:
        print("Running in SIMULATE mode.")
        run_simulated()
    else:
        print("Running with hardware serial:", SERIAL_PORT)
        run_hardware()