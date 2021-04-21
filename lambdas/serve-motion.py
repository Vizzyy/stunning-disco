import base64
import json
import os
import boto3 as boto3
import pymysql

ssm = boto3.client('ssm')
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


def lambda_handler(event=None, context=None):
    print(f"Event: {event}")

    db = pymysql.connect(host=SECRETS["HUB_HOST"],
                         user=SECRETS["database"]["DB_USER"],
                         password=SECRETS["database"]["DB_PASS"],
                         database=SECRETS["database"]["DB_USER"],
                         port=SECRETS["database"]["DB_PORT"],
                         ssl_ca='/tmp/db-cert',
                         cursorclass=pymysql.cursors.DictCursor)

    cursor = db.cursor()
    print("DB connection initiated.")
    sql = "select * from images order by id desc limit 0,1"
    cursor.execute(sql)
    results = cursor.fetchone()

    result = {
        'statusCode': 200,
        'isBase64Encoded': True,
        'headers': {
            'Content-Type': 'image/gif'
        },
        'body': base64.b64encode(results["Image"]).decode('utf-8'),
    }

    return result


if os.environ.get('ENV') == "dev":
    lambda_handler()
