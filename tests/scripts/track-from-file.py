"""
  Loads track data from a local file.
"""
import logging
from ski.io.track import TrackFileLoader


TEST_DATA_FILE = 'tests/testdata/ski_unittest.yaml'

# Set up logger
log = logging.getLogger(__name__)
logging.basicConfig()
log.setLevel(logging.INFO)


# Create track loader
ldr = TrackFileLoader(TEST_DATA_FILE)
track = ldr.get_track()

log.info('Loaded track: %s', track)
