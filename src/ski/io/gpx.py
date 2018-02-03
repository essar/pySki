"""
  Module providing functions and classes for reading GPX files.

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (04 Feb 2015)
"""

from xml.dom.minidom import Node, parse
from datetime import datetime

from pytz import timezone, utc
from ski.gps import GPSPoint

__author__ = 'Steve Roberts'
__version__ = 1.0


class GPXFile:
    """
    Class holding GPX file metadata.
    """

    def __init__(self):

        self.file_name = None

        self.max_tracks = 0
        self.track_count = 0

        self.tz = None  # Should use OS TZ as default


def __parse_meta():
    return NotImplemented


def __parse_track_point(gpx_file, tp):

    p = GPSPoint()

    if tp.nodeType == Node.ELEMENT_NODE:

        # Read attributes
        p.lat = float(tp.getAttribute("lat"))
        p.lon = float(tp.getAttribute("lon"))

        # Read elements
        p.a = __read_float(tp, "ele")
        p.s = __ms_to_kph(__read_float(tp, "speed"))
        p.ts = datetime.strptime(__read_text(tp, "time"), "%Y-%m-%dT%H:%M:%SZ")\
            .replace(tzinfo=utc).astimezone(gpx_file.tz)

        gpx_file.track_count += 1

    return p


def __ms_to_kph(ms):
    """
    Convert metres per second to kilometres per hour.
    :param ms: speed in metres per second
    :return: speed in kilometers per hour
    """
    return (ms * 60 * 60) / 1000


def __read_float(elem, tag_name):
    """
    Read a value from an XML element and return as a float.
    :param elem: parent XML element
    :param tag_name: XML element name
    :return: element value
    """
    t = __read_text(elem, tag_name)
    if t is None:
        return 0.0

    return float(t)


def __read_text(elem, tag_name):
    """
    Read a value from an XML element.
    :param elem: parent XML element
    :param tag_name: XML element name
    :return: element value
    """
    for e in elem.getElementsByTagName(tag_name):
        for ee in e.childNodes:
            if ee.nodeType == Node.TEXT_NODE:
                return ee.nodeValue

    return None


def parse_gpx_file(file_name, gpx_file=GPXFile()):
    """
    Read a GPX file and parse a list of GPSPoints.
    :param file_name: path to GPX file
    :param gpx_file: Optional GPXFile specifying file metadata.
    :return: list of GPSPoints.
    """
    f = open(file_name)
    doc = parse(f)
    gps = list(map(lambda e: __parse_track_point(gpx_file, e), doc.getElementsByTagName("trkpt")))
    f.close()

    return gps


if __name__ == '__main__':

    gpx = GPXFile()
    gpx.tz = timezone("US/Mountain")

    tps = parse_gpx_file("../../../../data/ski_20130214_sjr.gpx", gpx)
    print("Parsed {} points".format(len(tps)))
    print(tps[0])

