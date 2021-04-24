import base64
import datetime
import json
import boto3
import os
import urllib3
from urllib3 import Retry
from urllib3.exceptions import MaxRetryError

ssm = boto3.client('ssm')
sqs = boto3.client('sqs')
paginator = ssm.get_paginator('get_parameters_by_path')
iterator = paginator.paginate(Path=os.environ.get('SSM_PATH'), WithDecryption=True)
params = []
file_dir = "/tmp"

for page in iterator:
    params.extend(page['Parameters'])
    for param in page.get('Parameters', []):
        # Load all SSM params into environment
        os.environ[param.get('Name').split('/')[-1]] = param.get('Value')

# Write SSL client cert/key into container
with open(f'{file_dir}/lambda-cert.crt', 'w') as file:
    file.write(os.environ["lambda-cert"])

with open(f'{file_dir}/lambda-key.crt', 'w') as file:
    file.write(os.environ["lambda-key"])

with open(f'{file_dir}/db-cert.crt', 'w') as file:
    file.write(os.environ["db-cert"])

secrets = json.loads(os.environ.get('secrets'))
proxy_host = secrets["HUB_HOST"]
print(f"proxy_host: {proxy_host}")

conn = urllib3.connection_from_url(
    f'https://{proxy_host}',
    cert_file=f'{file_dir}/lambda-cert.crt',
    key_file=f'{file_dir}/lambda-key.crt'
)


def sqs_send(start_time: datetime, target_route: str, success: bool = True):
    queue_url = os.environ["queue-url"]
    now = datetime.datetime.now()
    elapsed = now - start_time
    elapsed_ms = elapsed.total_seconds() * 1000  # elapsed milliseconds
    full_path = target_route.split(proxy_host)[1].split('?')[0].split('/')
    full_path = [x for x in full_path if x]
    print(full_path)
    path = f"/{full_path[0]}/{full_path[1]}"

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
    target_route = f'https://{proxy_host}'

    try:
        print("Event:")
        print(event)

        method = event["httpMethod"]
        body = event["body"]
        query_params = event["queryStringParameters"]
        path = event["path"]
        body_params = {}
        query_param_string = ""

        if body is not None:
            body = base64.b64decode(body).decode('utf-8')
            print(f"Body: {body}")
            temp_params = body.split("&")
            for key_val in temp_params:
                temp_params = key_val.split("=")
                body_params[str(temp_params[0])] = str(temp_params[1])

        if query_params is not None:
            query_param_string += "?"
            query_param_array = []
            for key in query_params.keys():
                query_param_array.append(f"{key}={query_params[key]}")
            query_param_string += "&".join(query_param_array)

        target_route += path + query_param_string

        print(f"Checking route: {target_route} by method: {method}, body_params: {body_params}")

        response = conn.request_encode_body(method, target_route, fields=body_params, encode_multipart=False,
                                            timeout=5.0, retries=Retry(total=3))
    except MaxRetryError as max_e:
        print(f"Could not establish connection to hub: {max_e}")
        sqs_send(start_time, target_route, False)
        raise
    except Exception as e:
        print(f"Unknown error making request: {e}")
        sqs_send(start_time, target_route, False)
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
        sqs_send(start_time, target_route, False)
        raise RuntimeError

    sqs_send(start_time, target_route, True)

    return result


if os.environ.get('ENV') == "dev":
    # Run natively during development
    lights_two = {
        "resource": "/lights/{proxy+}",
        "path": "/lights/light2",
        "httpMethod": "GET",
        "headers": {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.5",
            "dnt": "1",
            "sec-gpc": "1",
            "te": "trailers",
            "upgrade-insecure-requests": "1",
        },
        "queryStringParameters": {
            "status": "true"
        },
        "pathParameters": {
            "proxy": "light1"
        },
        "stageVariables": None,
        "body": None,
        "isBase64Encoded": False
    }

    lambda_handler(lights_two)
