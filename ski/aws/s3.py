'''

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
'''

import boto3
from io import BytesIO, TextIOWrapper

#https://s3.eu-west-2.amazonaws.com/essar-zephyr-test/gsd/testdata.gsd
bucket = 'essar-zephyr-test'
testkey = 'gsd/testdata.gsd'

s3 = boto3.resource('s3')

class S3File:

	def __init__(self, key, download=False):
		# Get the S3 object
		self.obj = s3.Object(bucket, key)

		# Download the body content if requested
		self.body = None
		if download:
			self.download_body()


	def download_body(self):
		# Only download the body if it's not already been done
		if self.body is None:
			buf = BytesIO(self.obj.get()['Body'].read())
			self.body = TextIOWrapper(buf)

		# Reset stream
		self.body.seek(0)


	def __str__(self):
		return 's3://{:s}/{:s}'.format(self.obj.bucket_name, self.obj.key)


if __name__ == "__main__":
	s3f = S3File(testkey)
	print('Object {:s}; size {:d}, modified {:s}'.format(testkey, s3f.obj.content_length, s3f.obj.last_modified))
