#!/bin/bash

FUNC_NAME="stunning-disco"

while [ -n "$1" ]
do
  case "$1" in
    -d) echo "Deleting existing stack: $FUNC_NAME"; \
      aws cloudformation delete-stack --stack-name $FUNC_NAME; \
      echo "Waiting for stack deletion to finish..."; \
      aws cloudformation wait stack-delete-complete --stack-name $FUNC_NAME ;;
    *) echo "$1 is not an option" ;;
  esac
  shift
done

echo "Packaging template..."
sam package --s3-bucket vizzyy-packaging --output-template-file packaged.yml

echo "Deploying new stack..."
sam deploy --template-file packaged.yml --stack-name $FUNC_NAME --capabilities CAPABILITY_IAM && echo "Finished deploying!"

rm packaged.yml
echo "Finished cleanup."
