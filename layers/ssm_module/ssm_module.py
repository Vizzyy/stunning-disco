import os
import boto3

ssm = boto3.client('ssm')
paginator = ssm.get_paginator('get_parameters_by_path')
iterator = paginator.paginate(Path=os.environ.get('SSM_PATH'), WithDecryption=True)

for page in iterator:
    for param in page.get('Parameters', []):
        # Load all SSM params into environment
        os.environ[param.get('Name').split('/')[-1]] = param.get('Value')

# Write SSL client cert/key into container
with open(f'/tmp/lambda-cert.crt', 'w') as file:
    file.write(os.environ["lambda-cert"])

with open(f'/tmp/lambda-key.crt', 'w') as file:
    file.write(os.environ["lambda-key"])

with open(f'/tmp/db-cert.crt', 'w') as file:
    file.write(os.environ["db-cert"])