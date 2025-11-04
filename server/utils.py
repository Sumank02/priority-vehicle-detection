import math

def haversine(lat1, lon1, lat2, lon2):
    """Distance in meters between two lat/lon points."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def initial_bearing(lat1, lon1, lat2, lon2):
    """Initial bearing from point1 to point2 in degrees (0..360)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dlambda) * math.cos(phi2)
    y = math.cos(phi1)*math.sin(phi2) - math.sin(phi1)*math.cos(phi2)*math.cos(dlambda)
    bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
    return bearing

def direction_from_bearing(bearing):
    """
    Map bearing to an approach axis for a 2-way intersection:
    - around 0/180 => NS
    - around 90/270 => EW
    """
    # normalize to closest of {0,90,180,270}
    candidates = {"NS": [0, 180], "EW": [90, 270]}
    def min_delta(targets):
        return min(min(abs(bearing - t), 360-abs(bearing - t)) for t in targets)
    return "NS" if min_delta(candidates["NS"]) <= min_delta(candidates["EW"]) else "EW"