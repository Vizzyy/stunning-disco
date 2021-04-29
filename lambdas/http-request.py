import base64
import datetime
import json
import os
import urllib.parse
import sys
import urllib3
from urllib3 import Retry
from urllib3.exceptions import MaxRetryError

if os.environ.get('ENV') == "dev":
    # These modules are imported as Lambda Layers in prod
    # So we emulate something similar in development
    sys.path.insert(1, '../layers/sqs_module')
    sys.path.insert(1, '../layers/ssm_module')

from sqs_module import *
from ssm_module import *

secrets = json.loads(os.environ.get('secrets'))
proxy_host = secrets["HUB_HOST"]
sqs_queue = os.environ["queue-url"]

conn = urllib3.connection_from_url(
    f'https://{proxy_host}',
    cert_file=f'/tmp/lambda-cert.crt',
    key_file=f'/tmp/lambda-key.crt'
)


def lambda_handler(event=None, context=None):
    start_time = datetime.datetime.now()
    target_route = f'https://{proxy_host}'

    try:
        print(event)

        method = event["httpMethod"]
        body = event["body"]
        query_params = event["queryStringParameters"]
        path = event["path"]
        body_params = {}
        query_param_string = ""

        if body is not None:
            body_params = urllib.parse.parse_qs(base64.b64decode(body).decode('utf-8'))

        if query_params is not None:
            query_param_string += urllib.parse.urlencode(query_params)

        target_route += path + "?" + query_param_string

        print(f"Checking route: {target_route}, by method: {method}, with body_params: {body_params}")

        response = conn.request_encode_body(method, target_route, fields=body_params, encode_multipart=False,
                                            timeout=5.0, retries=Retry(total=3))
    except MaxRetryError as max_e:
        print(f"Could not establish connection to hub: {max_e}")
        sqs_send(sqs_queue, proxy_host, start_time, target_route, False)
        raise
    except Exception as e:
        print(f"Unknown error making request: {e}")
        sqs_send(sqs_queue, proxy_host, start_time, target_route, False)
        raise

    result = {
        'statusCode': response.status,
        'body': str(response.data.decode('utf-8')),
        'isBase64Encoded': False,
        'headers': {
            "Content-Type": "application/json"
        }
    }

    print(f"Result: {result}")

    if result['statusCode'] != 200:
        print("Encountered Server Error.")
        print(vars(response))
        sqs_send(sqs_queue, proxy_host, start_time, target_route, False)
        raise RuntimeError

    sqs_send(sqs_queue, proxy_host, start_time, target_route, True)

    return result


if os.environ.get('ENV') == "dev":
    # Run natively during development
    event = {
        "resource": "/lights/{proxy+}",
        "path": "/inside/custom",
        "httpMethod": "GET",
        "queryStringParameters": {"colorValue": "#FFFFFF"},
        "pathParameters": {
            "proxy": "light1"
        },
        "stageVariables": None,
        "body": None,
        "isBase64Encoded": False
    }

    lambda_handler(event)
