"""
  Module providing functions for working with AWS DynamoDB.
"""
import logging

from boto3 import client, resource
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import DYNAMODB_CONTEXT
from decimal import Inexact, Rounded, localcontext
from datetime import datetime
from ski.config import config
from ski.data.commons import ExtendedGPSPoint, debug_point_event
from ski.io.db import DataStore

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

db_endpoint = config['db']['dynamo']['endpoint_url']
db_table_points = config['db']['dynamo']['points_table_name']

# Initialise dynamodb resource
ddb = resource('dynamodb', endpoint_url=db_endpoint)


class DynamoDataStore(DataStore):
    """A datastore backed by DynamoDB."""

    def __init__(self):
        self.insert_count = 0
        self.error_count = 0

    def add_points_to_track(self, track, points):
        # Get Dynamo table
        table = ddb.Table(db_table_points)

        # Write points to the table in batches
        with table.batch_writer() as batch:
            # Write all points in track
            for point in points:
                try:
                    # Create item
                    item = build_item(track, point)
                    # Add item to batch
                    response = batch.put_item(Item=item)
                    self.insert_count += 1
                    debug_point_event(log, point, 'add_points_to_track: put_item %s=%s', track.track_id, response)
                except Exception as e:
                    # Something went wrong, log the error
                    log.error(e)
                    self.error_count += 1

    def get_track_points(self, track, offset=0, length=-1):
        # Get dynamo table
        table = ddb.Table(db_table_points)

        points = []
        try:

            # Retrieve batch of points based on track ID
            response = table.query(
                Select='ALL_ATTRIBUTES',
                KeyConditionExpression=Key('track_id').eq(track.track_id)
            )

            count = response['Count']
            log.debug('Found %d points in %s for %s', count, db_table_points, track.track_id)

            items = response['Items']

            for i in items:
                log.debug('Item=%s', i)

                p = ExtendedGPSPoint()
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
                    p.x = decimal_to_integer(ext['x'])
                    p.y = decimal_to_integer(ext['y'])
                    p.dst = decimal_to_float(ext['dst'])
                    p.hdg = decimal_to_float(ext['hdg'])
                    p.alt_d = decimal_to_integer(ext['alt_d'])
                    p.spd_d = decimal_to_float(ext['spd_d'])
                    p.hdg_d = decimal_to_float(ext['hdg_d']) 

                log.debug('point=%s', p)
                
                points.append(p)

        except Exception as e:
            # Something went wrong, log the error
            log.error(e)

        return points


def build_item(track, point):

    item = {
        'track_id': track.track_id,
        'timestamp': point.ts,
        'local_time': timestamp_to_local_time(point.ts, track),
        'track_group': track.track_group,
        'track_properties': track.properties,
        'gps': {
            'lat': float_to_decimal(point.lat),
            'lon': float_to_decimal(point.lon),
            'x': point.x,
            'y': point.y,
            'alt': point.alt,
            'spd': float_to_decimal(point.spd)
            },
        'ext': {
            'dst': float_to_decimal(point.dst),
            'hdg': float_to_decimal(point.hdg),
            'alt_d': point.alt_d,
            'spd_d': float_to_decimal(point.spd_d),
            'hdg_d': float_to_decimal(point.hdg_d)
            }
    }
    # Add windows
    for k in list(point.windows):
        # Get the window
        w = point.windows[k]
        win_obj = {
            'period': w.period,
            'distance': float_to_decimal(w.distance),
            'alt_delta': w.alt_delta,
            'alt_gain': w.alt_gain,
            'alt_loss': w.alt_loss,
            'alt_max': w.alt_max,
            'alt_min': w.alt_min,
            'speed_ave': float_to_decimal(w.speed_ave),
            'speed_delta': float_to_decimal(w.speed_delta),
            'speed_max': float_to_decimal(w.speed_max),
            'speed_min': float_to_decimal(w.speed_min)
        }
        key_str = 'win_{:s}'.format(str(k))
        item[key_str] = win_obj

    return item


def count_points():
    """Count the number of records created in the points table."""
    try:
        # Get Dynamo table
        table = ddb.Table(db_table_points)

        row_count = 0
        last_key = None

        while True:
            request = {'Select': 'COUNT'}
            if last_key is not None:
                request['ExclusiveStartKey'] = last_key

            response = table.scan(**request)
            log.debug('COUNT FROM %s: %s', db_table_points, response)

            row_count += response['Count']
            last_key = response['LastEvaluatedKey'] if 'LastEvaluatedKey' in response else None

            if last_key is None:
                break

        log.info('Point count=%s', row_count)
    except Exception as e:
        # Something went wrong, log the error
        log.error(e)


def create_table_points():
    """Create the points table."""
    try:
        response = ddb.create_table(
            TableName=db_table_points,
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

        log.debug('CREATE TABLE %s: %s', db_table_points, response)

    except ValueError as e:
        # Something went wrong, log the error
        log.error('Unable to create table %s: %s', db_table_points, e)


def init_db():
    """Initialise the database, creating tables as necessary."""
    try:
        ddb_client = client('dynamodb', endpoint_url=db_endpoint)

        response = ddb_client.describe_table(TableName=db_table_points)
        log.info('Table %s OK', response['Table']['TableName'])
    except ddb_client.exceptions.ResourceNotFoundException:
        create_table_points()
        log.info('Created table %s', db_table_points)


def decimal_to_float(decimal):
    """ Convert a decimal to a native floating point value"""
    return float(decimal)


def decimal_to_integer(decimal):
    """ Convert a decimal to a native integer value"""
    return int(decimal)


def format_datetime(dt):
    return dt.isoformat()


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

        return decimal_value


def timestamp_to_local_time(ts, track):
    return format_datetime(datetime.fromtimestamp(ts, track.start_time.tzinfo))