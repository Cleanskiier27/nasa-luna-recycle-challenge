import math

def calculate_inverse(p1_x, p1_y, p2_x, p2_y):
    """Calculate distance and bearing between two points."""
    dx = p2_x - p1_x
    dy = p2_y - p1_y
    distance = math.sqrt(dx**2 + dy**2)
    bearing = math.degrees(math.atan2(dx, dy))
    if bearing < 0:
        bearing += 360
    return distance, bearing

def calculate_traverse(p1_x, p1_y, distance, bearing):
    """Calculate coordinates of a new point from distance and bearing."""
    rad = math.radians(bearing)
    p2_x = p1_x + distance * math.sin(rad)
    p2_y = p1_y + distance * math.cos(rad)
    return p2_x, p2_y

def intersection_bearing_bearing(p1_x, p1_y, b1, p2_x, p2_y, b2):
    """Calculate intersection point of two bearings."""
    r1 = math.radians(b1)
    r2 = math.radians(b2)
    
    # Line equations: x = p1_x + t*sin(r1), y = p1_y + t*cos(r1)
    # y - p1_y = cot(r1) * (x - p1_x) -> x*cos(r1) - y*sin(r1) = p1_x*cos(r1) - p1_y*sin(r1)
    
    # Solving for (x, y)
    denom = math.sin(r1 - r2)
    if abs(denom) < 1e-9:
        return None # Parallel
        
    t1 = ((p2_x - p1_x) * math.cos(r2) - (p2_y - p1_y) * math.sin(r2)) / denom
    ix = p1_x + t1 * math.sin(r1)
    iy = p1_y + t1 * math.cos(r1)
    
    return ix, iy

if __name__ == "__main__":
    # Quick test
    d, b = calculate_inverse(0, 0, 10, 10)
    print(f"Inverse: Distance={d:.2f}, Bearing={b:.2f}")
    nx, ny = calculate_traverse(0, 0, d, b)
    print(f"Traverse: X={nx:.2f}, Y={ny:.2f}")
