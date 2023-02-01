

def enrich_point_with_alt_delta(window: MovingWindow, point: dict) -> dict:
    # Add point to window
    window.add_point(point)

    # Get alt delta
    alt_delta = window.delta('alt')
    print(f'alt_d={alt_delta}')

    # Enrich point
    point['alt_d'] = alt_delta

    return point

def enrich_point_with_distance_and_heading(window: MovingWindow, point: dict) -> dict:
    # Add point to window
    window.add_point(point)

    # Get distance
    dist = hypot(window.delta('x'), window.delta('y'))
    calc_spd = (dist / window.delta('ts')) if window.delta('ts') > 0 else 0

    # Get heading
    hdg = degrees(atan2(window.delta('x'), window.delta('y')))
    print(f'dist={dist}; hdg={hdg}; calc_spd={calc_spd}')

    # Enrich point
    point['d'] = dist
    point['hdg'] = hdg

    return point