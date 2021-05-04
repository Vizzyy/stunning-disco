import datetime
import os
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TableName')
table_object = dynamodb.Table(table_name)


def lambda_handler(event=None, context=None):
    print(f"Incoming event: {event}")

    try:
        subject = event["requestContext"]["identity"]["clientCert"]["subjectDN"]
        path = event["path"]
        cn = subject.split(',')[0].split('CN=')[1]
    except Exception:
        print("Could not parse details from client certificate.")
        raise

    stored_object = {
        'Id': str(uuid.uuid4()),
        'Timestamp': str(datetime.datetime.now()),
        'Principal': cn,
        'Path': path,
        'QueryParams': None,
        'Body': None
    }

    if cn != "lambda" and ("/api" in path or "/streams" in path) and "status" not in path:
        if "queryStringParameters" in event.keys():
            stored_object["QueryParams"] = event["queryStringParameters"]

        if "body" in event.keys():
            stored_object["Body"] = event["body"]

        response = table_object.put_item(
            Item=stored_object
        )

        print(f"Stored event into table: {response}")
    else:
        print(f"Will not log stored_object: {stored_object}")

    authorizer_response = {
        "principalId": cn,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "*"
                }
            ]
        },
        "context": {  # present in request context of lambda proxy integration -> event["requestContext"]["authorizer"]
            "key": "value",
            "numKey": 1,
            "boolKey": True
        }
    }

    print(f"Returning authorizer_response: {authorizer_response}")

    return authorizer_response


if os.environ.get('ENV') == "dev":

    request = {
        "type": "REQUEST",
        "resource": "/api/lights/light2",
        "path": "/api/lights/light2",
        "httpMethod": "GET",
        "queryStringParameters": {},
        "pathParameters": {},
        "requestContext": {
            "resourcePath": "/user",
            "httpMethod": "GET",
            "path": "/user",
            "protocol": "HTTP/1.1",
            "stage": "Prod",
            "identity": {
                "clientCert": {
                    "issuerDN": "CN=barney,OU=barney",
                    "validity": {
                        "notAfter": "Nov 26 23:44:27 2021 GMT",
                        "notBefore": "Nov 26 23:44:27 2020 GMT"
                    },
                    "subjectDN": "CN=barney,OU=barney"
                },
            },
        }
    }

    lambda_handler(request)
