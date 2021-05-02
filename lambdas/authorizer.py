import os


def lambda_handler(event=None, context=None):
    print(event)

    try:
        subject = event["requestContext"]["identity"]["clientCert"]["subjectDN"]
        cn = subject.split(',')[0].split('CN=')[1]
    except Exception:
        print("Could not parse details from client certificate.")
        raise

    authorizer_reponse = {
        "principalId": cn,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "*"
                }
            ]
        },
        "context": {  # these should get passed directly into downstream lambdas via "content" param of handler
            "key": "value",
            "numKey": 1,
            "boolKey": True
        }
    }

    print(authorizer_reponse)

    return authorizer_reponse


if os.environ.get('ENV') == "dev":

    request = {
        "type": "REQUEST",
        "resource": "/user",
        "path": "/user",
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
