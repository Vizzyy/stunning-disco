import os


def lambda_handler(event=None, context=None):
    print(event)

    response = {
        'statusCode': 200,
        'body': "test",
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'application/json'
        }
    }

    print(response)

    return response


if os.environ.get('ENV') == "dev":
    lambda_handler()
