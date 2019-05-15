"""
  Test script for ski.aws.s3.

  Downloads a resource.
"""
import logging

from ski.aws.s3 import *

# Set up logger
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

TEST_DATA_S3 = 'gsd/testdata.gsd'


s3f = S3File(TEST_DATA_S3)
print('{0}; size {1}, modified {2}'.format(s3f, s3f.obj.content_length, s3f.obj.last_modified))
