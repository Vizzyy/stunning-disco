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

db = pymysql.connect(host=SECRETS["HUB_HOST"],
                     user=SECRETS["database"]["DB_USER"],
                     password=SECRETS["database"]["DB_PASS"],
                     database=SECRETS["database"]["DB_USER"],
                     port=SECRETS["database"]["DB_PORT"],
                     ssl_ca='/tmp/db-cert',
                     cursorclass=pymysql.cursors.DictCursor)

cursor = db.cursor()
print("DB connection initiated.")


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

    image_blob = results["Image"]
    encoded_image = base64.b64encode(image_blob).decode('utf-8')
    print(f"image_blob size: {len(image_blob)}, encoded_image size: {len(encoded_image)}")
    # len of encoded_image like 100 bytes needs to be < 6291556 bytes

    result = {
        'statusCode': 200,
        'isBase64Encoded': True,
        'headers': {
            'Content-Type': 'image/gif'
        },
        'body': encoded_image,
    }

    return result


if os.environ.get('ENV') == "dev":

    offset_param = 1

    test_event = {
        'resource': '/streams/motion/blob', 'path': '/streams/motion/blob', 'httpMethod': 'GET',
        'headers': {
            'accept': 'image/webp,*/*', 'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.5', 'dnt': '1', 'Host': 'something',
            'referer': 'https://something/streams/motion?', 'sec-gpc': '1', 'te': 'trailers',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0',
            'X-Forwarded-For': '0.0.0.0'
        },
        'queryStringParameters': {
            'offset': f'{offset_param}'
        },
        'body': None,
        'isBase64Encoded': False
    }

    response = lambda_handler(test_event)
    response["body"] = response["body"][0:90]
    print(response)
