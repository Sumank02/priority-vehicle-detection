import json, sys, os
sys.path.append(os.path.abspath("."))

from server.server import app

def test_vehicle_endpoint():
    client = app.test_client()
    payload = {"id": "TEST1", "lat": 12.9715, "lon": 77.5944, "speed": 40}
    r = client.post("/api/vehicle", json=payload)
    assert r.status_code == 200
    data = r.get_json()
    assert "status" in data
    assert "distance_m" in data