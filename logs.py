import datetime
import os
import boto3
import uuid
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TableName')
table = dynamodb.Table(table_name)


def lambda_handler(event=None, context=None):
    print(f"Incoming event: {event}")

    # scan_kwargs = {
    #     'FilterExpression': Key('year').
    # }

    response = table.scan().get('Items')
    print(response)

    return response


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
