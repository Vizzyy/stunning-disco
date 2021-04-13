#!/bin/bash

FUNC_NAME=$1

zip -r lambda_function.zip lambda_function.py
aws lambda update-function-code --function-name "$FUNC_NAME" --zip-file fileb://lambda_function.zip
rm lambda_function.zip

#trigger function
#aws lambda invoke --function-name "$FUNC_NAME" output.json