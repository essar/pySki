"""
  Module containing classes for loading GPS data from GPX files.
"""
import logging
import time

from datetime import datetime
from ski.aws.s3 import S3File
from ski.data.commons import BasicGPSPoint
from ski.logging import increment_stat, log_point
from xml.dom.minidom import parse, parseString

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

stats = {}

default_batch = 64


class GPXSource:
    """
    Load GPX formatted data.
    """
    def __init__(self, source, batch_size=default_batch):
        self.source = source
        self.batch_size = batch_size
        # Set up array and internal pointer
        self.elems = []
        self.elem_ptr = 0

    def load_data(self, doc):
        """
        Load data from a GPX document.

        Params:
          doc: the XML document containing GPX data.
        """
        # Extract elements from document
        doc_elems = doc.getElementsByTagName('trkpt')
        log.debug('%d elements found', len(doc_elems))
        self.elems.extend(doc_elems)

    def load_points(self):
        """Load all the GPS points from a GPX document."""
        # Prepare a new array
        points = []

        # Get next element from document, return if no points remain
        if self.elem_ptr < len(self.elems):  # and (batch_size < 0 or self.elem_ptr < batch_size):
            # Look elements
            s = self.elem_ptr
            e = self.elem_ptr + self.batch_size
            elems = self.elems[s:e]
            # Increment pointer
            self.elem_ptr += len(elems)
        else:
            return None

        for elem in elems:
            parsed_point = parse_gpx_elem(elem)

            # Write to pointlog
            log_point(parsed_point.ts, 'Point load from GPX', source=self.source, **parsed_point.values())

            # Add the point to output
            points.append(parsed_point)

        # Return points array
        return points


class GPXFileSource(GPXSource):
    """Load GPX data from a local file."""
    def __init__(self, gpx_file_handle, batch_size=default_batch):
        super().__init__(gpx_file_handle.name, batch_size)

        log.debug('Loading GPX data from local file (%s)', gpx_file_handle.name)
        self.load_data(parse(gpx_file_handle))


class GPXS3Source(GPXSource):
    """Load GPX data from a resource on S3."""
    def __init__(self, s3_file_handle, batch_size=default_batch):
        if type(s3_file_handle) != S3File:
            raise TypeError('s3_file parameter must be an S3File')
        super().__init__(s3_file_handle.name, batch_size)

        log.debug('Loading GPX data from S3 (%s)', s3_file_handle.name)
        self.load_data(parse(s3_file_handle))


class GPXStringSource(GPXSource):
    """Load GSD data from a provided String."""
    def __init__(self, gpx_string, batch_size=default_batch):
        super().__init__('string', batch_size)
        
        log.debug('Loading GPX data from string (%d bytes)', len(gpx_string))
        self.load_data(parseString(gpx_string))


def __get_text(elem):
    rc = []
    for e in elem:
        if e.nodeType == e.TEXT_NODE:
            rc.append(e.data)
    return ''.join(rc)


def __get_alt(elem):
    return __get_text(elem.getElementsByTagName('ele')[0].childNodes)


def __get_lat(elem):
    return elem.getAttribute('lat')


def __get_lon(elem):
    return elem.getAttribute('lon')


def __get_speed(elem):
    return __get_text(elem.getElementsByTagName('speed')[0].childNodes)


def __get_ts(elem):
    return __get_text(elem.getElementsByTagName('time')[0].childNodes)


def parse_gpx_elem(elem):
    """Parse an element of GPX data for a GPS point."""
    # Get next element from document, return if no points remain
    if elem is None:
        return None

    # Read data from XML element
    xml_lat = __get_lat(elem)
    xml_lon = __get_lon(elem)
    xml_ts = __get_ts(elem)
    xml_alt = __get_alt(elem)
    xml_spd = __get_speed(elem)
    log.debug('XML: lat=%s; lon=%s; ts=%s; alt=%s; spd=%s', xml_lat, xml_lon, xml_ts, xml_alt, xml_spd)
        
    point = BasicGPSPoint()
    
    try:
        # GPX datetime in YYYY-MM-DDTHH:MM:SSZ (UTC) format
        dt = datetime.strptime(xml_ts, '%Y-%m-%dT%H:%M:%SZ')
        # Convert to timestamp
        point.ts = int(datetime.timestamp(dt))
        
        # Parse latitude, convert to floating point
        point.lat = float(xml_lat)
            
        # Parse longitude, convert to floating point
        point.lon = float(xml_lon)    
            
        # GPX altitude in metres, convert from floating point to int
        point.alt = int(float(xml_alt))

        # GPX speed is m/s, convert to km/h
        point.spd = (float(xml_spd) * 3600.0) / 1000.0
                
    except ValueError as e:
        log.warning('Failed to parse GPX element: %s; %s', elem.toxml(), e)
        
    # Return data item
    return point


def parse_gpx(gpx_source, **kwargs):

    start_time = time.time()

    # Prepare a new array
    points = gpx_source.load_points()

    end_time = time.time()
    increment_stat(stats, 'process_time', (end_time - start_time))
    increment_stat(stats, 'point_count', len(points) if points is not None else 0)

    # Return points array
    return points
