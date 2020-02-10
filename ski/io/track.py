"""

"""
import logging
import yaml

from contextlib import closing
from pytz import timezone
from ski.data.commons import Track
from ski.aws.s3 import load_track_from_s3

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class TrackLoader:

    def __init__(self):
        self.track = None

    def load_data(self, data):
        track_id = data['id']
        track_group = data['group']

        tz = timezone(data['timezone'])
        start_time = data['start_time'].astimezone(tz)

        datafile = data['datafile']

        self.track = Track(track_id, track_group, start_time, datafile)
        self.track.properties = data['properties']

    def get_track(self):
        return self.track


class TrackFileLoader(TrackLoader):
    """"""

    def __init__(self, track_file):
        super().__init__()

        with open(track_file, 'r') as f:
            log.info('Loading track from local file (%s)', track_file)
            self.load_data(yaml.load(f))


class TrackS3Loader(TrackLoader):

    def __init__(self, s3_object_key):
        super().__init__()

        with(closing(load_track_from_s3(s3_object_key))) as f:
            self.load_data(yaml.load(f, Loader=yaml.SafeLoader))
            log.info('Loaded track from S3 (%s): %s', s3_object_key, self.track)
