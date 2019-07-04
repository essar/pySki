"""
  Test script for ski.aws.dynamo.

  Initialises the database.
"""
import logging

from ski.aws.dynamo import *

# Set up logger
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# Initialise the database
init_db()
count_points()