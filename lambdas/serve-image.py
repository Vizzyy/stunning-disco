import base64
import boto3
import os

s3 = boto3.resource('s3')


def lambda_handler(event=None, context=None):
    resource = event["path"][1:]
    bucket = os.environ.get('BUCKET_NAME')
    image = s3.Object(bucket, resource)
    img_data = image.get().get('Body').read()

    print(f"Event: {event}")
    print(f"Resource: {resource}, Bucket: {bucket}")

    result = {
        'statusCode': 200,
        'body': base64.b64encode(img_data),
        'isBase64Encoded': True,
        'headers': {
            'Content-Type': 'image/png'
        }
    }

    print(f"Result: {result}")

    return result


if os.environ.get('ENV') == "dev":
    image = "test.png"

    event = {
        'resource': '/image', 'path': f'/{image}', 'httpMethod': 'GET',
        'headers': {
            'accept': 'image/webp,*/*', 'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.5', 'cache-control': 'max-age=0'
        },
        'body': None,
        'isBase64Encoded': True
    }

    lambda_handler(event)
