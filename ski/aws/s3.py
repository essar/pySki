"""
  Module providing functions for working with AWS Simple Storage Service (S3).
"""
import logging
from boto3 import resource
from io import BytesIO, TextIOWrapper
from ski.config import config

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

bucket = config['dataloader']['aws']['source_bucket']

# Initialise s3 resource
s3 = resource('s3')

class S3File:
    """A file resource held in AWS S3."""
    def __init__(self, key, download=False):
        # Get the S3 object
        self.obj = s3.Object(bucket, key)

        # Download the body content if requested
        self.body = None
        if download:
            self.download_body()


    def download_body(self, force_download=False):
        """Download the content (body) of the file from S3."""
        # Only download the body if it's not already been done
        if self.body is None or force_download:
            buf = BytesIO(self.obj.get()['Body'].read())
            log.debug('Downloaded S3 body')
            self.body = TextIOWrapper(buf)

        # Reset stream
        self.body.seek(0)


    def __str__(self):
        return 's3://{:s}/{:s}'.format(self.obj.bucket_name, self.obj.key)
