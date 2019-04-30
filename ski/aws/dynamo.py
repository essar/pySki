'''

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
'''

import logging

from boto3 import client, resource
from boto3.dynamodb.types import DYNAMODB_CONTEXT
from decimal import Decimal, Inexact, Rounded, localcontext
from ski.config import config
from ski.io.db import DataStore

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

db_points = config['aws']['dynamo']['points_table_name']

# Initialise dynamodb resource
dynamodb = resource('dynamodb', endpoint_url='http://dynamo:8000')


class DynamoDataStore(DataStore):

	def __init__(self):
		self.insert_count = 0
		self.error_count = 0


	def add_point_to_track(self, track, point):
		# Get Dynamo table
		table = dynamodb.Table(db_points)

		log.debug('Storing point: %s', point)

		dec_lat = float_to_decimal(point.lat)
		dec_lon = float_to_decimal(point.lon)
		dec_spd = float_to_decimal(point.spd)

		try:
			response = table.put_item(
				Item={
					'track_id': track.track_id,
					'timestamp': point.ts,
					'track_group': track.track_group,
					'track_info': {},
					'gps': {
						'lat': dec_lat,
						'lon': dec_lon,
						'alt': point.alt,
						'spd': dec_spd
					}
				}
			)

			self.insert_count += 1
			log.debug('put_item %s=%s', track.track_id, response)
		except Exception as e:
			log.error(e)
			self.error_count += 1


	def add_points_to_track(self, track, points):
		# Get Dynamo table
		table = dynamodb.Table(db_points)

		with table.batch_writer() as batch:
			for point in points:
				log.debug('Storing point: %s', point)

				dec_lat = float_to_decimal(point.lat)
				dec_lon = float_to_decimal(point.lon)
				dec_spd = float_to_decimal(point.spd)

				try:
					response = batch.put_item(
						Item={
							'track_id': track.track_id,
							'timestamp': point.ts,
							'track_group': track.track_group,
							'track_info': {},
							'gps': {
								'lat': dec_lat,
								'lon': dec_lon,
								'alt': point.alt,
								'spd': dec_spd
							}
						}
					)
					self.insert_count += 1
					log.debug('put_item %s=%s', track.track_id, response)
				except Exception as e:
					log.error(e)


def count_points():
	try:
		# Get Dynamo table
		table = dynamodb.Table(db_points)
		response = table.scan(
			Select='COUNT'
		)
		log.info('Point count=%s', response['Count'])
	except Exception as e:
		log.error(e)


def create_table_tracks():
	try:
		response = dynamodb.create_table(
			TableName='zephyr-tracks',
			KeySchema=[
				{
					'AttributeName': 'track_id',
					'KeyType': 'HASH'
				}
			],
			AttributeDefinitions=[
				{
					'AttributeName': 'track_id',
					'AttributeType': 'S'
				}
			],
			ProvisionedThroughput={
				'ReadCapacityUnits': 1,
				'WriteCapacityUnits': 1
			},
			BillingMode='PAY_PER_REQUEST'
		)

		log.info(response)

	except ValueError as e:
		log.error('Unable to create zephyr-tracks table: %s', e)


def create_table_points():
	try:
		response = dynamodb.create_table(
			TableName=db_points,
			KeySchema=[
				{
					'AttributeName': 'track_id',
					'KeyType': 'HASH'
				},
				{
					'AttributeName': 'timestamp',
					'KeyType': 'RANGE'
				}
			],
			AttributeDefinitions=[
				{
					'AttributeName': 'track_id',
					'AttributeType': 'S'
				},
				{
					'AttributeName': 'timestamp',
					'AttributeType': 'N'
				}
			],
			BillingMode='PAY_PER_REQUEST'
		)

		log.info(response)

	except ValueError as e:
		log.error('Unable to create %s table: %s', db_points, e)


def init_db():

	try:
		ddb_client = client('dynamodb', endpoint_url='http://dynamo:8000')

		response = ddb_client.describe_table(TableName='zephyr-points')
		log.info('Table %s OK', response['Table']['TableName'])
	except ddb_client.exceptions.ResourceNotFoundException:
		log.info('Table %s does not exist', db_points)
		create_table_points()


def float_to_decimal(float_value):
	"""
	Convert a floating point value to a decimal that DynamoDB can store,
	and allow rounding.
	"""

	# Perform the conversion using a copy of the decimal context that boto3
	# uses. Doing so causes this routine to preserve as much precision as
	# boto3 will allow.
	with localcontext(DYNAMODB_CONTEXT) as cxt:
		# Allow rounding
		cxt.traps[Inexact] = 0
		cxt.traps[Rounded] = 0
		decimal_value = cxt.create_decimal_from_float(float_value)
		log.debug('float_to_decimal: float=%f, decimal=%f', float_value, decimal_value)

		return decimal_value


if __name__ == "__main__":
	logging.basicConfig()
	init_db()
	count_points()

