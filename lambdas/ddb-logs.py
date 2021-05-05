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


def lambda_handler(event=None, context=None):
    print(f"Incoming event: {event}")

    log_data = query_table("barney")

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

    lambda_handler()
