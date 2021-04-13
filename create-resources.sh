#!/bin/bash

FUNC_NAME="stunning-disco"

echo "Deleting existing stack: $FUNC_NAME"
aws cloudformation delete-stack --stack-name $FUNC_NAME # delete stack

#zip -r lambda_function.zip availability-canary.py mysql* google proto* six* -q
echo "Packaging template..."
sam package --s3-bucket vizzyy-packaging --output-template-file packaged.yml
echo "Waiting for stack deletion to finish..."
aws cloudformation wait stack-delete-complete --stack-name $FUNC_NAME
echo "Deploying new stack..."
sam deploy --template-file packaged.yml --stack-name $FUNC_NAME --capabilities CAPABILITY_IAM && echo "Finished deploying!"

#rm lambda_function.zip
rm packaged.yml
echo "Finished cleanup."
