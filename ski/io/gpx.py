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
log.setLevel(logging.DEBUG)

stats = {}

default_batch = 64


class GPXSource:
    """
    Class providing operations for loading and parsing GPX-formatted files and streams.
    """

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
        """
        Initialise the source with the specified stream.
        @param stream: an `io` stream that provides the data for the source.
        """

        self.stream = stream
        self.stream_iter = iterparse(stream)

        log.info('Initialised GPX source: %s', self)

    def load_points(self):
        """
        Reads a set of points from the source. For GPX files this is the specified number of points.
        @return: a list of points.
        """
        # Prepare a new array
        points = []

        for elem in self.next_section_iter():

            parsed_point = parse_gpx_elem(elem)
            if parsed_point is not None:
                # Add the point to output
                points.append(parsed_point)

                # Write to point log
                log_point(parsed_point.ts, 'Point load from GPX', source=self.url, **parsed_point.values())

        # Return points array
        return points

    def next_section_iter(self):
        """
        Returns an iterator over the next set of data.
        @return: an iterator over the data.
        """

        point_count = 0
        while point_count < self.batch_size:
            event, elem = self.stream_iter.__next__()
            if elem.tag.endswith('trkpt'):
                yield elem
                point_count += 1

        log.debug('next_section_iter: point_count=%d', point_count)
        return


def __find_text_or_raise(elem, tag):
    ns = '{http://www.topografix.com/GPX/1/0}'
    e = elem.find(ns + tag)
    if e is None:
        raise ValueError('Tag {0} not found in element {1}'.format(tag, elem.tag))
    return e.text


def parse_gpx_elem(elem):
    """
    Parses an element of GPX data for a GPS point.
    @param elem: GPX element
    @return a BasicGPSPoint containing the parsed data or None if a GPS point cannot be parsed.
    """
    # Get next element from document, return if no points remain

    # Empty line in is empty output
    if elem is None:
        return None

    log.debug('parse_gpx_elem: elem=%s; children=%s', elem, list(elem))

    point = BasicGPSPoint()

    try:
        # Read data from XML element
        xml_lat = elem.attrib['lat']
        xml_lon = elem.attrib['lon']
        xml_ts = __find_text_or_raise(elem, 'time')
        xml_alt = __find_text_or_raise(elem, 'ele')
        xml_spd = __find_text_or_raise(elem, 'speed')

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
        log.warning('Failed to parse GPS data from GPX element: %s; %s', elem, e)
        return None
        
    # Return data item
    return point


def parse_gpx(gpx_source, **kwargs):
    """
    Parse a GPX source.
    @param gpx_source: the source to parse.
    @param kwargs: Additional parameters.
    @return: a list of points.
    """

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
