import os

redirect_path = os.environ.get('REDIRECT_URL')


def lambda_handler(event=None, context=None):
    return {
        'statusCode': 302,
        'headers': {
            'Location': redirect_path,
        }
    }


if os.environ.get('ENV') == "dev":
    print(lambda_handler())
