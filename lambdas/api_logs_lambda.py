import datetime
import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TableName')
table = dynamodb.Table(table_name)


def query_table(principal, page_size=25, page_num=1, reverse=False):
    query_expression = Key('Principal').eq(principal)
    # & Key('Timestamp').lt(datetime.datetime.now().__str__())

    response = table.query(
        KeyConditionExpression=query_expression,
        ScanIndexForward=reverse,
        Limit=page_size*page_num
    )

    # print(response)

    results = response['Items'][page_size*page_num-25:page_size*page_num]

    # [print(item) for item in response['Items']]

    return results


def scan_table(hours=0, days=0, page_size=25, page_num=1):

    time_delta = datetime.timedelta(hours=hours, days=days)
    timestamp_parameter = datetime.datetime.now() - time_delta
    scan_kwargs = {
        'FilterExpression': Key('Timestamp').gt(timestamp_parameter.__str__()),
    }

    results = []
    done = False
    start_key = None
    while not done:
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key
        response = table.scan(**scan_kwargs)
        results += response["Items"]
        start_key = response.get('LastEvaluatedKey', None)
        done = start_key is None

    results.sort(key=lambda asset: asset["Timestamp"], reverse=True)

    # [print(item) for item in results]

    return results[page_size*page_num-25:page_size*page_num]


def lambda_handler(event=None, context=None):
    print(f"Incoming event: {event}")

    log_data = scan_table(days=1)

    result = {
        'statusCode': 200,
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(log_data),
    }

    print(result)

    return result


if os.environ.get('ENV') == "dev":

    event = {
        "resource": "/api/logs",
        "path": "/api/logs",
        "httpMethod": "GET",
        "queryStringParameters": {
            "days": "0",
            "hours": "12",
            "page_num": "1",
            "page_size": "25",
            "principal": "barney",
            "reversed": "false"
        },
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "authorizer": {
                "numKey": "1",
                "principalId": "barney",
                "integrationLatency": 173,
                "key": "value",
                "boolKey": "true"
            }
        },
        "body": None,
        "isBase64Encoded": False
    }

    lambda_handler()
