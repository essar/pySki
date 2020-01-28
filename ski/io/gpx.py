"""
  Module containing classes for loading GPS data from GPX files.
"""
import logging
import time

from datetime import datetime
from ski.data.commons import BasicGPSPoint
from ski.logging import increment_stat, log_point
from xml.etree.ElementTree import iterparse

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

stats = {}

default_batch = 64


class GPXSource:

    def __init__(self, url, batch_size=default_batch):

        self.url = url
        self.batch_size = batch_size

        self.stream = None
        self.stream_iter = None

        # Set up array and internal pointer
        self.elems = []
        self.elem_ptr = 0

    def __repr__(self):
        return '<{0} url={1}; stream={2}; elem_count={3}>'.format(
            type(self).__name__, self.url, self.stream, len(self.elems))

    def init_stream(self, stream):

        self.stream = stream
        self.stream_iter = iterparse(stream)

        log.info('Initialised GPX source: %s', self)

    def next_section_iter(self):

        point_count = 0
        while point_count < self.batch_size:
            event, elem = self.stream_iter.__next__()
            if elem.tag.endswith('trkpt'):
                yield elem
            point_count += 1

        return

    def load_points(self):
        """Load GPS points from a GPX document."""
        # Prepare a new array
        points = []

        for elem in self.next_section_iter():

            parsed_point = parse_gpx_elem(elem)

            # Add the point to output
            points.append(parsed_point)

            # Write to pointlog
            log_point(parsed_point.ts, 'Point load from GPX', source=self.url, **parsed_point.values())

        # Return points array
        return points


def __get_text(elem):
    rc = []
    for e in elem:
        if e.nodeType == e.TEXT_NODE:
            rc.append(e.data)
    return ''.join(rc)


def parse_gpx_elem(elem):
    """Parse an element of GPX data for a GPS point."""
    # Get next element from document, return if no points remain

    # Empty line in is empty output
    if elem is None:
        return None

    log.debug('parse_gpx_elem: elem=%s; children=%s', elem, list(elem))

    # Read data from XML element
    xml_lat = elem.attrib['lat']
    xml_lon = elem.attrib['lon']
    xml_ts = elem.find('{http://www.topografix.com/GPX/1/0}time').text
    xml_alt = elem.find('{http://www.topografix.com/GPX/1/0}ele').text
    xml_spd = elem.find('{http://www.topografix.com/GPX/1/0}speed').text

    point = BasicGPSPoint()
    
    try:
        # GPX datetime in YYYY-MM-DDTHH:MM:SSZ (UTC) format
        dt = datetime.strptime(xml_ts, '%Y-%m-%dT%H:%M:%SZ')
        # Convert to timestamp
        point.ts = int(datetime.timestamp(dt))
        log.debug('parse_gpx_elem: xml_ts=%s, dt=%s, ts=%d', xml_ts, dt, point.ts)
        
        # Parse latitude, convert to floating point
        point.lat = float(xml_lat)
        log.debug('parse_gpx_elem: xml_lat=%s, lat=%.4f', xml_lat, point.lat)
            
        # Parse longitude, convert to floating point
        point.lon = float(xml_lon)
        log.debug('parse_gpx_elem: xml_lon=%s, lon=%.4f', xml_lon, point.lon)
            
        # GPX altitude in metres, convert from floating point to int
        point.alt = int(float(xml_alt))
        log.debug('parse_gpx_elem: xml_alt=%s, alt=%d', xml_alt, point.alt)

        # GPX speed is m/s, convert to km/h
        point.spd = (float(xml_spd) * 3600.0) / 1000.0
        log.debug('parse_gpx_elem: xml_spd=%s, spd=%.2f', xml_spd, point.spd)
                
    except ValueError as e:
        log.warning('Failed to parse GPS data from GPX element: %s; %s', elem.toxml(), e)
        
    # Return data item
    return point


def parse_gpx(gpx_source, **kwargs):

    log.debug('parse_gpx: source=%s, args=%s', gpx_source, kwargs)

    start_time = time.time()

    # Prepare a new array
    points = gpx_source.load_points()

    end_time = time.time()
    process_time = end_time - start_time
    point_count = len(points) if points is not None else 0

    increment_stat(stats, 'process_time', process_time)
    increment_stat(stats, 'point_count', point_count)

    log.info('Phase complete %s', {
        'phase': 'load (GPX)',
        'point_count': point_count,
        'process_time': process_time
    })

    # Return points array
    return points
