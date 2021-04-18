import base64
import datetime
import json

import boto3
import os
import urllib3

# Setup outside of handler so it only executes once per container
from urllib3 import Retry
from urllib3.exceptions import MaxRetryError

ssm = boto3.client('ssm')
sqs = boto3.client('sqs')

paginator = ssm.get_paginator('get_parameters_by_path')
iterator = paginator.paginate(Path=os.environ.get('SSM_PATH'), WithDecryption=True)
params = []

for page in iterator:
    params.extend(page['Parameters'])
    for param in page.get('Parameters', []):
        # Load all SSM params into environment
        os.environ[param.get('Name').split('/')[-1]] = param.get('Value')
        # print(param.get('Value'))

# Write SSL client cert/key into container
with open('/tmp/lambda-cert', 'w') as file:
    file.write(os.environ["lambda-cert"])

with open('/tmp/lambda-key', 'w') as file:
    file.write(os.environ["lambda-key"])

with open('/tmp/db-cert', 'w') as file:
    file.write(os.environ["db-cert"])

conn = urllib3.connection_from_url(
    os.environ.get('lambda-availability-host'),
    cert_file='/tmp/lambda-cert',
    key_file='/tmp/lambda-key'
)


def sqs_send(start_time: datetime, target_route: str, success: bool = True):
    queue_url = os.environ["queue-url"]
    now = datetime.datetime.now()
    elapsed = now - start_time
    elapsed_ms = elapsed.total_seconds() * 1000  # elapsed milliseconds
    path = target_route.split(".com")[1]

    message = {
        "action": "insert",
        "table": "canary_metrics",
        "values": {
            "path": path,
            "ms_elapsed": elapsed_ms,
            "timestamp": now.__str__(),
            "success": success
        }
    }

    # Send message to SQS queue
    print("Pushing message to queue...")
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=(json.dumps(message)))
    print(message)
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise RuntimeError("Could not enqueue message!")


def lambda_handler(event=None, context=None):
    start_time = datetime.datetime.now()
    try:
        print("Event:")
        print(event)
        body = base64.b64decode(event["body"]).decode('utf-8')
        print(f"Body: {body}")

        query_params = body.split("&")
        param_map = {}
        for key_val in query_params:
            query_param = key_val.split("=")
            param_map[str(query_param[0])] = str(query_param[1])

        target_route = f"{os.environ.get('lambda-availability-host')}"
        method = "POST"

        if "light" in param_map.keys():
            target_route = f"{target_route}/lights"
            if param_map["light"] == "2":
                target_route += "/bedroom/lamp"
            elif param_map["light"] == "1":
                target_route += "/bedroom/xmas"
            elif param_map["light"] == "3":
                target_route += "/strip/inside"
            elif param_map["light"] == "4":
                target_route += "/strip/outside"
        else:
            target_route = f"{target_route}/door/{param_map['status']}"
            method = "GET"

        print(f"Checking route: {target_route} by method: {method}")
        print(param_map)
        print(param_map["status"])

        response = conn.request_encode_body(method, target_route, fields=param_map, encode_multipart=False,
                                            timeout=5.0, retries=Retry(total=3))
    except MaxRetryError as max_e:
        print(f"Could not establish connection to hub: {max_e}")
        sqs_send(start_time, target_route, False)
        raise RuntimeError
    except Exception as e:
        print(f"Unknown error making request: {e}")
        sqs_send(start_time, target_route, False)
        raise RuntimeError

    result = {
        'statusCode': response.status,
        'body': str(response.data),
        'isBase64Encoded': False,
        'headers': {
            "Content-Type": "application/json"
        }
    }

    print(f"Result status: {result['statusCode']}")

    if result['statusCode'] != 200:
        print("Encountered Server Error.")
        print(vars(response))
        sqs_send(start_time, target_route, False)
        raise RuntimeError

    sqs_send(start_time, target_route, True)

    return result


if os.environ.get('ENV') == "dev":
    # Run natively during development
    event = {'resource': '/lights/toggle', 'path': '/lights/toggle', 'httpMethod': 'POST',
             'body': 'light=1&status=false', 'isBase64Encoded': False}

    event2 = {'resource': '/door/toggle', 'path': '/door/toggle', 'httpMethod': 'POST',
              'body': 'status=open&entry=OPENED%3A+OVERRIDE+BY+UI', 'isBase64Encoded': False}

    lambda_handler(event)
