"""
"""
import logging

from ski.logging import debug_point_event, log_json
from ski.data.commons import EnrichedWindow
from ski.loader.window import PointWindow


# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def enrich_batch(batch, default_keys, min_head_length=0):

    # Create a window from points in the batch
    window = PointWindow(head=batch.body, tail=batch.tail, min_head_length=min_head_length)

    # Enrich points in the window
    return enrich_points(window, default_keys)


def enrich_points(window, default_keys):

    # Initialize output
    output = []

    # Iterate through the window
    while window.process():
        # Get current point from the window
        point = window.target_point

        # Process all windows
        for k in default_keys:
            # Extract window points using window key
            window_points = window.extract(*k.key())
            # Calculate the enriched values for this set of points
            enriched_values = get_enriched_data(window_points)
            debug_point_event(log, window.target_point, 'Enriched data (%s): %s', k, enriched_values)

            # Save enriched values to the point
            window.target_point.windows[k] = EnrichedWindow(**enriched_values)

        # Add enriched point to output
        output.append(point)

    # Return enriched points
    return output


def __avg(values):
    return float(sum(values)) / max(1, len(values))


def get_enriched_data(points):
    # Build a dict of enriched values
    data = {
        'distance': distance(points),
        'alt_delta': alt_delta(points),
        'alt_gain': alt_cuml_gain(points),
        'alt_loss': alt_cuml_loss(points),
        'alt_max': alt_max(points),
        'alt_min': alt_min(points),
        'speed_min': speed_min(points),
        'speed_max': speed_max(points),
        'speed_ave': speed_ave(points),
        'speed_delta': speed_delta(points)
    }
    return data


def alt_delta(points):
    return points[-1].alt - points[0].alt


def alt_cuml_gain(points):
    return sum([p.alt_d for p in points if p.alt_d > 0])


def alt_cuml_loss(points):
    return sum([p.alt_d for p in points if p.alt_d < 0])


def alt_max(points):
    return max([p.alt for p in points])


def alt_min(points):
    return min([p.alt for p in points])


def distance(points):
    return sum([p.dst for p in points])


def speed_ave(points):
    return __avg([p.spd for p in points])


def speed_delta(points):
    return points[-1].spd - points[0].spd


def speed_max(points):
    return max([p.spd for p in points])


def speed_min(points):
    return min([p.spd for p in points])
