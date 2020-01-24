"""
  Module providing functions for working with AWS Simple Storage Service (S3).
"""
import logging
from boto3 import resource
from codecs import decode
from io import TextIOBase, TextIOWrapper
from ski.config import config

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

bucket = config['dataloader']['aws']['source_bucket']

# Initialise s3 resource
s3 = resource('s3')


class BufferedS3Response(TextIOBase):

    def __init__(self, body):
        self.body = body
        self.body_iter = body.iter_lines()

    def __repr__(self):
        return '<{0}>'.format(type(self).__name__)

    def close(self):
        self.body.close()

    def readline(self, size=-1):
        return decode(self.body_iter.__next__()) + '\n'


def load_source_from_s3(source):

    # Get the object from S3
    obj = s3.Object(bucket, source.url)

    rsp = obj.get()
    log.debug('s3 get_object %s', rsp)

    # Create the stream
    stream = BufferedS3Response(rsp['Body'])

    # Init the stream
    source.init_stream(stream)

    return stream
