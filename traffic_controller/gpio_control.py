"""
Hardware abstraction for traffic lights.
- SIMULATE=True: prints states to console
- SIMULATE=False: uses RPi.GPIO pins mapping
"""

import os, time

SIMULATE = os.getenv("SIMULATE", "true").lower() == "true"

PINS = {
    "NS_RED": 17,
    "NS_YELLOW": 27,
    "NS_GREEN": 22,
    "EW_RED": 23,
    "EW_YELLOW": 24,
    "EW_GREEN": 25
}

if not SIMULATE:
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        for pin in PINS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)
    except Exception as e:
        print("GPIO init failed, falling back to SIMULATE:", e)
        SIMULATE = True

def set_signal(ns_green=False, ew_green=False):
    if SIMULATE:
        print(f"[CTRL] NS_GREEN={ns_green} | EW_GREEN={ew_green}")
        return

    # Real GPIO
    GPIO.output(PINS["NS_GREEN"], 1 if ns_green else 0)
    GPIO.output(PINS["NS_RED"], 0 if ns_green else 1)
    GPIO.output(PINS["NS_YELLOW"], 0)
    GPIO.output(PINS["EW_GREEN"], 1 if ew_green else 0)
    GPIO.output(PINS["EW_RED"], 0 if ew_green else 1)
    GPIO.output(PINS["EW_YELLOW"], 0)

def cleanup():
    if not SIMULATE:
        import RPi.GPIO as GPIO
        GPIO.cleanup()