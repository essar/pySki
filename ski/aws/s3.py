"""
  Module providing functions for working with AWS Simple Storage Service (S3).
"""
import logging
from boto3 import resource
from codecs import decode
from io import TextIOBase
from ski.config import config

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

bucket = config['aws']['s3']['source_bucket']

# Initialise s3 resource
s3 = resource('s3')


class BufferedS3Response(TextIOBase):
    """
    Wrapper class around Botocore StreamingResponse objects to implement additional methods for streaming.
    """

    def __init__(self, body):
        self.body = body
        self.body_iter = body.iter_lines()

    def __repr__(self):
        return '<{0}>'.format(type(self).__name__)

    def close(self):
        """
        Closes the underlying stream.
        """
        self.body.close()

    def read(self, size=None):
        """
        Reads bytes from the underlying stream.
        @param size: Optional number of bytes to read, or read to end of stream.
        @return: an array of bytes.
        """
        return self.body.read(size)

    def readline(self, size=-1):
        """
        Reads a line of data from the underlying stream.
        @param size: Optional number of lines to read.
        @return: the next line in the file, including trailing newline character.
        """
        return decode(self.body_iter.__next__()) + '\n'


def load_source_from_s3(source):
    """
    Loads data into source object and initialises the source stream.
    @param source: the source object to load into.
    @return: reference to the initialised stream.
    """

    # Get the object from S3
    obj = s3.Object(bucket, source.url)

    rsp = obj.get()
    log.debug('load_source_from_s3: source=%s, rsp=%s', source, rsp)

    # Create the stream
    stream = BufferedS3Response(rsp['Body'])

    # Init the stream
    source.init_stream(stream)

    return stream
