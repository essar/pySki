"""
  Module providing functions for working with AWS DynamoDB.
"""
import logging

from boto3 import client, resource
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import DYNAMODB_CONTEXT
from decimal import Decimal, Inexact, Rounded, localcontext
from ski.config import config
from ski.data.commons import ExtendedGPSPoint
from ski.io.db import DataStore

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

db_endpoint = config['db']['dynamo']['endpoint_url']
db_points   = config['db']['dynamo']['points_table_name']

# Initialise dynamodb resource
dynamodb = resource('dynamodb', endpoint_url=db_endpoint)


class DynamoDataStore(DataStore):
    """A datastore backed by DynamoDB."""
    def __init__(self):
        self.insert_count = 0
        self.error_count = 0


    def __build_item(self, track, point):

        extended = None
        if type(point) == ExtendedGPSPoint:
            extended = {
                'x'     : point.x,
                'y'     : point.y,
                'dst'   : float_to_decimal(point.dst),
                'hdg'   : float_to_decimal(point.hdg),
                'alt_d' : point.alt_d,
                'spd_d' : float_to_decimal(point.spd_d),
                'hdg_d' : float_to_decimal(point.hdg_d)
            }

        item = {
            'track_id'    : track.track_id,
            'timestamp'   : point.ts,
            'track_group' : track.track_group,
            'track_info'  : {},
            'gps': {
                'lat' : float_to_decimal(point.lat),
                'lon' : float_to_decimal(point.lon),
                'alt' : point.alt,
                'spd' : float_to_decimal(point.spd)
            },
            'extended' : extended
        }

        return item


    def add_points_to_track(self, track, points):
        # Get Dynamo table
        table = dynamodb.Table(db_points)

        with table.batch_writer() as batch:
            for point in points:
                log.debug('Storing point: %s', point)

                try:
                    item = self.__build_item(track, point)
                    log.debug('add_points_to_track: item=%s', item)

                    response = batch.put_item(Item=item)
                    self.insert_count += 1
                    log.debug('add_points_to_track: put_item %s=%s', track.track_id, response)
                except Exception as e:
                    log.error(e)
                    self.error_count += 1


    def get_track_points(self, track, offset=0, length=-1):
        # Get dynamo table
        table = dynamodb.Table(db_points)

        # Retrieve batch of points based on track ID

        points = []
        try:

            response = table.query(
                Select='ALL_ATTRIBUTES',
                KeyConditionExpression=Key('track_id').eq(track.track_id)
            )

            count = response['Count']
            log.info('Found %d points in %s for %s', count, db_points, track.track_id)

            items = response['Items']

            for i in items:
                log.debug('Item=%s', i)

                p = EnrichedPoint()
                p.ts = decimal_to_integer(i['timestamp'])
                p.track_id = i['track_id']
                
                # GPS Sub object
                gps = i['gps']
                p.lat = decimal_to_float(gps['lat'])
                p.lon = decimal_to_float(gps['lon'])
                p.alt = decimal_to_integer(gps['alt'])
                p.spd = decimal_to_float(gps['spd'])

                # Extended sub object
                if 'extended' in i:
                    ext = i['extended']
                    p.x     = decimal_to_integer(ext['x'])
                    p.y     = decimal_to_integer(ext['y'])
                    p.dst   = decimal_to_float(ext['dst'])
                    p.hdg   = decimal_to_float(ext['hdg'])
                    p.alt_d = decimal_to_integer(ext['alt_d'])
                    p.spd_d = decimal_to_float(ext['spd_d'])
                    p.hdg_d = decimal_to_float(ext['hdg_d']) 

                log.debug('point=%s', p)
                
                points.append(p)

        except Exception as e:
            log.error(e)

        return points


    def save_extended_points(self, points):
        # Get Dynamo table
        table = dynamodb.Table(db_points)

        with table.batch_writer() as batch:
            for point in points:
                log.debug('Storing point: %s', point)

                try:
                    item = {
                        'track_id' : point.track_id,
                        'timestamp': point.ts,
                        'extended' : {
                            'x'     : point.x,
                            'y'     : point.y,
                            'dst'   : float_to_decimal(point.dst),
                            'hdg'   : float_to_decimal(point.hdg),
                            'alt_d' : point.alt_d,
                            'spd_d' : float_to_decimal(point.spd_d),
                            'hdg_d' : float_to_decimal(point.hdg_d)
                        }
                    }
                    # Add windows
                    #item.update(point.windows)

                    response = batch.put_item(Item=item)
                    self.insert_count += 1
                    log.debug('put_item %s/%s=%s', point.track_id, point.ts, response)
                except Exception as e:
                    log.error(e)


def count_points():
    """Count the number of records created in the points table."""
    try:
        # Get Dynamo table
        table = dynamodb.Table(db_points)

        row_count = 0
        last_key = None

        while True:
            request = { 'Select' : 'COUNT' }
            if last_key is not None:
                request['ExclusiveStartKey'] = last_key

            response = table.scan(**request)
            log.debug('Scan response: %s', response)

            row_count += response['Count']
            last_key = response['LastEvaluatedKey'] if 'LastEvaluatedKey' in response else None

            if last_key is None:
                break

        log.info('Point count=%s', row_count)
    except Exception as e:
        log.error(e)



def create_table_points():
    """Create the points table."""
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
    """Initialise the database, creating tables as necessary."""
    try:
        ddb_client = client('dynamodb', endpoint_url=db_endpoint)

        response = ddb_client.describe_table(TableName=db_points)
        log.info('Table %s OK', response['Table']['TableName'])
    except ddb_client.exceptions.ResourceNotFoundException:
        log.info('Table %s does not exist', db_points)
        create_table_points()


def decimal_to_float(decimal):
    return float(decimal)


def decimal_to_integer(decimal):
    return int(decimal)


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
