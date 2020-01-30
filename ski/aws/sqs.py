"""
  Module providing functions for working with AWS Simple Storage Service (S3).
"""
import json
import logging
import time

from boto3 import resource
from ski.config import config
from ski.logging import increment_stat

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

stats = {}

enrich_queue_url = config['aws']['sqs']['enrich_queue_url']

# Initialise sqs resource
sqs = resource('sqs')


def sqs_process_batch(body, tail, drain, batch_idx, track):

    start_time = time.time()

    # Get SQS queue
    queue = sqs.Queue(enrich_queue_url)

    msg = json.dumps({
        'batch': batch_idx,
        'track': track.values(),
        'body': list(map(lambda x: x.values(), body)),
        'tail': list(map(lambda x: x.values(), tail))
    })

    if len(msg) > 256520:
        log.warning('SQS message exceeding suggested max size')

    try:
        rsp = queue.send_message(MessageBody=msg)
        log.debug('sqs_process_batch: batch_idx=%d, rsp=%s', batch_idx, rsp)

    except Exception as e:
        # Something went wrong, log the error
        log.error(e)

    end_time = time.time()
    increment_stat(stats, 'process_time', (end_time - start_time))
    increment_stat(stats, 'point_count', len(body))
    increment_stat(stats, 'msg_count', 1)
