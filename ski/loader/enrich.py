"""
"""
import logging
import time

from ski.logging import log_point, increment_stat, max_stat, min_stat
from ski.data.commons import EnrichedWindow


# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

stats = {}


def enrich_points(window, default_keys):

    start_time = time.time()

    # Initialize output
    output = []

    # Iterate through the window
    while window.process():
        # Get current point from the window
        point = window.target_point

        # Quick stats
        max_stat(stats, 'track_max_speed', point.spd)
        max_stat(stats, 'track_max_alt', point.alt)
        min_stat(stats, 'track_min_alt', point.alt)

        increment_stat(stats, 'track_total_distance', point.dst)
        if point.alt_d < 0:
            increment_stat(stats, 'track_total_desc', point.alt_d)
            increment_stat(stats, 'track_desc_distance', point.dst)

        # Process all windows
        for k in default_keys:
            # Extract window points using window key
            window_points = window.extract(*k.key())
            # Calculate the enriched values for this set of points
            enriched_values = get_enriched_data(window_points)
            log.debug('Enriched data (%s): %s', k, enriched_values)

            # Save enriched values to the point
            window.target_point.windows[k] = EnrichedWindow(**enriched_values)

            # Record in pointlog
            log_point(point.ts, 'Enrich', key=k, ts=point.ts, **enriched_values)

            # Quick stats
            k_sust = '{:s}_sust_spd'.format(str(k))
            max_stat(stats, k_sust, enriched_values['speed_min'])

        # Add enriched point to output
        output.append(point)

    end_time = time.time()
    process_time = end_time - start_time
    point_count = len(output)

    increment_stat(stats, 'process_time', process_time)
    increment_stat(stats, 'point_count', point_count)

    log.info('Phase complete %s', {
        'phase': 'enrich',
        'point_count': point_count,
        'process_time': process_time
    })

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
