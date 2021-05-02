import datetime
import json
import os
import boto3 as boto3
import sys
from botocore.exceptions import ClientError

if os.environ.get('ENV') == "dev":
    # These modules are imported as Lambda Layers in prod
    # So we emulate something similar in development
    sys.path.insert(1, '../layers/sqs_module')
    sys.path.insert(1, '../layers/ssm_module')

from sqs_module import *
from ssm_module import *

s3_client = boto3.client('s3')
SECRETS = json.loads(os.environ["secrets"])
proxy_host = SECRETS["HUB_HOST"]
sqs_queue = os.environ["queue-url"]
bucket = "vizzyy-motion-events"


def create_signed_url(object_name, expiration=60):
    try:
        request_params = {
            'Bucket': bucket,
            'Key': f"{object_name}"
        }
        return s3_client.generate_presigned_url('get_object', Params=request_params, ExpiresIn=expiration)
    except ClientError as e:
        print(e)
        raise


def lambda_handler(event=None, context=None):
    start_time = datetime.datetime.now()
    print(f"Event: {event}")
    offset = 0

    try:
        new_offset = int(event['queryStringParameters']['offset'])
        if new_offset > -1:
            offset = new_offset
    except Exception as e:
        print(e)

    try:
        bucket_contents = s3_client.list_objects(Bucket=bucket)['Contents']
        bucket_contents.sort(key=lambda asset: asset["Key"], reverse=True)
        asset_name = bucket_contents[offset]["Key"]
        signed_url = create_signed_url(asset_name)

        result = {
            'statusCode': 200,
            'isBase64Encoded': False,
            'headers': {
                'Content-Type': 'image/gif'
            },
            'body': signed_url,
        }

        sqs_send(sqs_queue, proxy_host, start_time, proxy_host+event["path"], True)

        return result
    except Exception as e:
        sqs_send(sqs_queue, proxy_host, start_time, proxy_host+event["path"], False)
        print(e)
        raise


if os.environ.get('ENV') == "dev":

    offset_param = 0

    test_event = {
        'resource': '/streams/motion', 'path': '/streams/motion', 'httpMethod': 'GET',
        'queryStringParameters': {
            'offset': f'{offset_param}'
        },
        'body': None,
        'isBase64Encoded': False
    }

    response = lambda_handler(test_event)
    print(response)
