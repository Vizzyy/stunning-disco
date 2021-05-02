import json
import os


def lambda_handler(event=None, context=None):
    print(event)
    try:
        authorizer = event["requestContext"]["authorizer"]
        print(f"authorizer: {authorizer}")
        issuer = event["requestContext"]["identity"]["clientCert"]["issuerDN"]
        subject = event["requestContext"]["identity"]["clientCert"]["subjectDN"]
        cn = subject.split(',')[0].split('CN=')[1]
        validity = event["requestContext"]["identity"]["clientCert"]["validity"]
    except Exception:
        print("Could not parse details from client certificate.")
        raise

    identity = json.dumps({
        "issuer": issuer,
        "subject": subject,
        "validity": validity,
        "commonName": cn,
    })

    response = {
        'statusCode': 200,
        'body': identity,
        'isBase64Encoded': False,
        'headers': {
            'Content-Type': 'application/json'
        }
    }

    print(response)

    return response


if os.environ.get('ENV') == "dev":
    event = {
        "requestContext": {
            "identity": {
                "clientCert": {
                    "issuerDN": "CN=lambda,OU=lambda",
                    "validity": {
                        "notAfter": "Nov 30 21:03:36 2021 GMT",
                        "notBefore": "Nov 30 21:03:36 2020 GMT"
                    },
                    "subjectDN": "CN=lambda,OU=lambda"
                },
            }
        }
    }

    lambda_handler(event)
