import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def calculate_bounding_box(lat, lon, radius_km):
    """
    Calculate bounding box coordinates for efficient database filtering
    Returns (min_lat, max_lat, min_lon, max_lon)
    """
    # Earth radius in km
    earth_radius = 6371
    
    # Latitude bounds (1 degree approx = 111 km)
    lat_change = radius_km / 111.0
    min_lat = lat - lat_change
    max_lat = lat + lat_change
    
    # Longitude bounds (adjust for latitude)
    lon_change = radius_km / (111.0 * math.cos(math.radians(lat)))
    min_lon = lon - lon_change
    max_lon = lon + lon_change
    
    return min_lat, max_lat, min_lon, max_lon