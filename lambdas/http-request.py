import base64

import boto3
import os
import urllib3

# Setup outside of handler so it only executes once per container
from urllib3 import Retry
from urllib3.exceptions import MaxRetryError

ssm = boto3.client('ssm')

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


def lambda_handler(event=None, context=None):
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
        raise RuntimeError
    except Exception as e:
        print(f"Unknown error making request: {e}")
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
        raise RuntimeError

    return result


if os.environ.get('ENV') == "dev":
    # Run natively during development
    event = {'resource': '/lights/toggle', 'path': '/lights/toggle', 'httpMethod': 'POST',
             'body': 'light=1&status=false', 'isBase64Encoded': False}

    event2 = {'resource': '/door/toggle', 'path': '/door/toggle', 'httpMethod': 'POST',
              'body': 'status=open&entry=OPENED%3A+OVERRIDE+BY+UI', 'isBase64Encoded': False}

    lambda_handler(event)
