"""

"""
import logging
import yaml

from pytz import timezone
from ski.data.commons import Track

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class TrackLoader:

    def __init__(self):
        self.track = None
        self.datafile = None

    def load_data(self, data):
        track_id = data['id']
        track_group = data['group']

        tz = timezone(data['timezone'])
        start_time = data['start_time'].astimezone(tz)

        self.track = Track(track_id, track_group, start_time)
        self.track.properties = data['properties']

        self.datafile = data['datafile']

    def get_track(self):
        return self.track


class TrackFileLoader(TrackLoader):
    """"""

    def __init__(self, track_file):
        super().__init__()

        with open(track_file, 'r') as f:
            log.info('Loading track from local file (%s)', track_file)
            self.load_data(yaml.load(f))

