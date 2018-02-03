"""
  Module providing functions and classes for writing JSON files.

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (04 Feb 2015)
"""

from datetime import datetime
from json import dump, JSONEncoder
from ski.tracks import TrackInfo, TrackPoint

__author__ = 'Steve Roberts'
__version__ = 1.0


class JSONTrackEncoder(JSONEncoder):
    """
    Class used for encoding objects to JSON.
    """

    def default(self, o):

        if isinstance(o, TrackPoint):
            return o.as_dict()

        if isinstance(o, TrackInfo):
            return o.as_dict()

        else:
            return JSONEncoder.default(self, o)


class JSONFile:
    """
    Class used for holding metadata about a JSON file.
    """

    def __init__(self):

        self.file_name = None


def write_track(file_name, track_info, track_data):
    """
    Writes a Track to a file in JSON format.
    :param file_name: the file to write JSON data to.
    :param track_info: a TrackInfo object that describes the track.
    :param track_data:  a TrackData object containing the track data.
    """

    # Open file
    fo = open(file_name, 'w')

    # Write header
    fo.write("// Essar Ski Data\n")
    fo.write("// Generated: {}\n".format(datetime.now()))
    fo.write("// Points: {}\n".format(len(track_data['points'])))

    fo.write("var trackInfo = ")
    dump(track_info, fo, indent=4, cls=JSONTrackEncoder)
    fo.write("\n")

    fo.write("var trackData = ")
    dump(track_data, fo, indent=4, cls=JSONTrackEncoder)
    fo.write("\n")

    fo.close()
