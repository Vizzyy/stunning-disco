import base64
import json
import os
import boto3 as boto3
import pymysql
from botocore.exceptions import ClientError

ssm = boto3.client('ssm')
s3_client = boto3.client('s3')
paginator = ssm.get_paginator('get_parameters_by_path')
iterator = paginator.paginate(Path=os.environ.get('SSM_PATH'), WithDecryption=True)
params = []

for page in iterator:
    params.extend(page['Parameters'])
    for param in page.get('Parameters', []):
        # Load all SSM params into environment
        os.environ[param.get('Name').split('/')[-1]] = param.get('Value')

SECRETS = json.loads(os.environ["secrets"])

with open('/tmp/db-cert', 'w') as file:
    file.write(os.environ["db-cert"])

db = pymysql.connect(host=SECRETS["HUB_HOST"],
                     user=SECRETS["database"]["DB_USER"],
                     password=SECRETS["database"]["DB_PASS"],
                     database=SECRETS["database"]["DB_USER"],
                     port=SECRETS["database"]["DB_PORT"],
                     ssl_ca='/tmp/db-cert',
                     cursorclass=pymysql.cursors.DictCursor)

cursor = db.cursor()
print("DB connection initiated.")


def create_signed_url(object_name, expiration=60):
    try:
        request_params = {
            'Bucket': "vizzyy-motion-events",
            'Key': f"{object_name}.gif"
        }
        return s3_client.generate_presigned_url('get_object', Params=request_params, ExpiresIn=expiration)
    except ClientError as e:
        print(e)
        raise


def lambda_handler(event=None, context=None):
    print(f"Event: {event}")

    offset = 0

    try:
        new_offset = int(event['queryStringParameters']['offset'])
        if new_offset > -1:
            offset = new_offset
    except Exception as e:
        print(e)

    sql = f"select * from images order by id desc limit {offset},1"
    cursor.execute(sql)
    results = cursor.fetchone()

    asset_name = results["Time"]
    signed_url = create_signed_url(asset_name)

    result = {
        'statusCode': 200,
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'image/gif'
        },
        'body': signed_url,
    }

    return result


if os.environ.get('ENV') == "dev":

    offset_param = 0

    test_event = {
        'resource': '/streams/motion/blob', 'path': '/streams/motion/blob', 'httpMethod': 'GET',
        'queryStringParameters': {
            'offset': f'{offset_param}'
        },
        'body': None,
        'isBase64Encoded': False
    }

    response = lambda_handler(test_event)
    print(response)
