### LED Intersection Modal Setup

This guide explains how to connect a simple LED road-intersection model so the correct lane turns green for a priority vehicle. This integration is optional and does not change default behavior unless enabled.

### What you will build
- Two directions: NS (North–South) and EW (East–West)
- Signals: at minimum 1 green LED per direction (optionally add red/yellow)
- Controller: the `traffic_controller` service drives GPIO pins; with hold mode enabled, the lane stays green until the vehicle passes

### Requirements
- Raspberry Pi with GPIO
- LEDs (2–6), 220–330 Ω resistors, wires, breadboard
- Python 3.10+, project dependencies installed (`pip install -r requirements.txt`)

### GPIO pin mapping (defaults)
- NS_RED: GPIO17
- NS_YELLOW: GPIO27
- NS_GREEN: GPIO22
- EW_RED: GPIO23
- EW_YELLOW: GPIO24
- EW_GREEN: GPIO25

You can change pins in `traffic_controller/gpio_control.py`.

### Wiring
- For each LED: GPIO pin -> resistor -> LED anode (+)
- LED cathode (−) -> Raspberry Pi GND
- Ensure a common ground; verify LED polarity (long leg is anode)

### Simulation vs hardware
The controller uses the `SIMULATE` environment variable. By default it simulates (no GPIO). To use real LEDs on the Pi, set `SIMULATE=false` when starting the controller.

Linux/macOS:
```bash
export SIMULATE=false
python -m traffic_controller.traffic_controller
```

PowerShell (Windows):
```powershell
$env:SIMULATE='false'
python -m traffic_controller.traffic_controller
```

### Enable hold-until-pass behavior (optional)
Edit `server/config.py`:
- Set `HOLD_UNTIL_PASS = True`
- Optionally tune thresholds:
  - `THRESHOLD_METERS` (engage)
  - `RELEASE_THRESHOLD_METERS` (release; default 240)

With hold enabled, the server calls the controller’s `/api/priority_hold` when within threshold and `/api/priority_release` once the vehicle has passed. If `HOLD_UNTIL_PASS = False` (default), the original duration-based behavior remains unchanged.

### Services
- `traffic_controller` (5001): drives LEDs; endpoints `/api/priority`, `/api/priority_hold`, `/api/priority_release`, `/api/state`
- `server` (5000): receives GPS, computes distance/bearing/axis, triggers controller
- `dashboard` (5100): shows last events and controller state
- `vehicle/*` simulators: `AMB001` (NS), `FIRT001` (EW)

### Start order (manual)
1) On the Pi (with LEDs), start controller with hardware:
```bash
export SIMULATE=false
python -m traffic_controller.traffic_controller
```
2) Start server (same Pi or another machine):
```bash
python -m server.server
```
3) Start dashboard:
```bash
python -m dashboard.app
```
4) Start one or both simulators:
```bash
python -m vehicle.vehicle_sim --repeat --interval 3 --jitter 0.5
python -m vehicle.firetruck_sim --repeat --interval 2.5 --jitter 0.4
```

### Notes
- With hold enabled, the selected axis stays green until distance exceeds `RELEASE_THRESHOLD_METERS`.
- Without hold, green is granted for `DEFAULT_PRIORITY_SECONDS` and normal cycling resumes.

### Troubleshooting
- If LEDs never change: verify `SIMULATE=false`, wiring, pins, and ground.
- GPIO permission errors: run with sufficient privileges on the Pi.
- Dashboard DISCONNECTED: ensure controller/server/dashboard are running.
- No priority events: ensure simulators run near the configured `INTERSECTION` in `server/config.py`.

### to test the Modal

1) Power off the Pi and wire LEDs as above, then power on.
2) On the Pi, run the controller with hardware:
```bash
export SIMULATE=false
python -m traffic_controller.traffic_controller
```
3) (Optional) In `server/config.py`, set `HOLD_UNTIL_PASS = True` and save.
4) Start backend and dashboard:
```bash
python -m server.server
python -m dashboard.app
```
5) Start at least one simulator:
```bash
python -m vehicle.vehicle_sim --repeat --interval 3 --jitter 0.5
```
6) Observe:
- Open http://127.0.0.1:5100 and watch status/metrics.
- Corresponding lane GREEN LED turns on (NS for AMB001, EW for FIRT001).
- With hold enabled, LED stays green until the vehicle passes; otherwise it times out per `DEFAULT_PRIORITY_SECONDS`.
7) Stop demo (Windows):
```powershell
taskkill /IM python.exe /F
```

### improvements

For Pi usage, only ensure:
- Update controller URLs in server/config.py to the Pi IP.
- Start controller with SIMULATE=false on the Pi.
- If dashboard/server run elsewhere, update SERVER/CTRL in dashboard/static/app.js.

These tips make the LED demo more reliable and easier to run, if You face any issue.

1) When your Raspberry Pi and your computer are different machines
- What this means: The Raspberry Pi is running the LED controller, and your computer is running the “server” and dashboard.
- Why this matters: The server needs to know how to reach the controller on the Pi. “127.0.0.1” means “this same computer,” so it will not work if the controller is on another device.
- What to do (one-time change):
  - Find your Pi’s IP address (example: 192.168.1.45).
  - Open `server/config.py` and change these lines to use your Pi’s IP:
    - `TRAFFIC_CONTROLLER_URL = "http://192.168.1.45:5001/api/priority"`
    - `TRAFFIC_CONTROLLER_HOLD_URL = "http://192.168.1.45:5001/api/priority_hold"`
    - `TRAFFIC_CONTROLLER_RELEASE_URL = "http://192.168.1.45:5001/api/priority_release"`
  - Save the file and restart the server.

2) If the dashboard webpage cannot reach the services
- What this means: The web page shows an error like “Failed to fetch” or “Disconnected.”
- Likely causes:
  - The services are not running yet (controller/server).
  - The addresses inside the dashboard are pointing to the wrong machine.
- Quick checks:
  - First, start the controller and the server and wait a few seconds.
  - Then refresh the dashboard page.
- If the dashboard is hosted on a different machine, update its addresses:
  - Open `dashboard/static/app.js` and set the top lines to match where your services run:
    - `const SERVER = "http://<server-machine-ip>:5000";`
    - `const CTRL   = "http://<pi-ip-address>:5001";`
  - Replace `<server-machine-ip>` and `<pi-ip-address>` with the actual numbers (like `192.168.1.20`).
  - Save the file and restart the dashboard.

3) Make the demo “hold green until the vehicle passes”
- What this means: Instead of turning green only for a fixed number of seconds, the light stays green until the vehicle has passed the intersection.
- Why it’s good for demos: More realistic and easier to see the behavior.
- How to enable:
  - Open `server/config.py` and set: `HOLD_UNTIL_PASS = True`
  - (Optional) Adjust when to start and stop:
    - `THRESHOLD_METERS` = distance to start giving priority
    - `RELEASE_THRESHOLD_METERS` = distance after passing where we release priority
  - Save the file and restart the server.

4) Optional: Less noisy dashboard when presenting
- What this means: The dashboard is set to developer mode (`debug=True`), which prints extra information.
- How to make it quieter:
  - Open `dashboard/app.py` and change the last line to remove `debug=True`, for example:
    - `app.run(host="0.0.0.0", port=5100)`
  - Save and restart the dashboard.

5) General reliability checklist
- Use good, snug connections on the breadboard, and a common GND for all LEDs.
- If the LEDs do nothing, confirm the Pi is set to hardware mode: start the controller with `SIMULATE=false` (see earlier section).
- If you move services between machines, always update the IP addresses as shown above.
- If something seems “stuck,” stop all windows and start again in this order: controller → server → dashboard → simulators.

