"""
  Loads track data from a local file.
"""
import logging
from ski.io.track import TrackS3Loader


TEST_TRACK_KEY = 'ski_unittest.yaml'

# Set up logger
log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel(logging.INFO)


# Create track loader
ldr = TrackS3Loader(TEST_TRACK_KEY)
track = ldr.get_track()

log.info('Loaded track: %s', track)
