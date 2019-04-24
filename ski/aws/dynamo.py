'''

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
'''

import logging

from boto3 import client, resource
from ski.io.db import DataStore

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Initialise dynamodb resource
dynamodb = resource('dynamodb')


class DynamoDataStore(DataStore):

	def __init__(self):
		pass


	def add_point_to_track(self, track, point):
		pass


def create_tables():
	pass


def check_tables():
	cli = client('dynamodb')
	response = cli.describe_table(TableName='zephyr-tracks')
	log.info(response)


if __name__ == "__main__":
	check_tables()
