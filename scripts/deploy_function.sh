#!/bin/bash

FUNC_NAME=$1

zip -r -j http-request.zip lambdas/http-request.py
aws lambda update-function-code --function-name "$FUNC_NAME" --zip-file fileb://http-request.zip
rm http-request.zip

#trigger function
#aws lambda invoke --function-name "$FUNC_NAME" output.json