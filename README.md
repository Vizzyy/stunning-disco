```bash
#!/bin/bash

FUNC_NAME="stunning-disco"

while [ -n "$1" ]
do
  case "$1" in
    -d) API_ID=`aws apigateway get-rest-apis --query 'items[].id' --output yaml | cut -c 3-`; \
      echo "Deleting existing stack ($API_ID): $FUNC_NAME"; \
      aws cloudformation delete-stack --stack-name $FUNC_NAME; \
      echo "Waiting for stack deletion to finish..."; \
      aws cloudformation wait stack-delete-complete --stack-name $FUNC_NAME; \
      aws logs delete-log-group --log-group-name API-Gateway-Execution-Logs_$API_ID/Prod ;;
    *) echo "$1 is not an option" ;;
  esac
  shift
done

./scripts/upload_web_src.sh

echo "Creating Lambda Zip(s)..."
zip -r -j http-request.zip lambdas/http-request.py
zip -r -j redirect.zip lambdas/redirect.py
zip -r -j serve-image.zip lambdas/serve-image.py

echo "Packaging template..."
sam package --s3-bucket vizzyy-packaging --output-template-file packaged.yml

echo "Deploying stack..."
sam deploy --template-file packaged.yml --stack-name $FUNC_NAME --capabilities CAPABILITY_IAM \
&& echo "Finished deploying!" || exit 1

echo "Updating lambda function(s)..."
aws lambda update-function-code --function-name "http-request" --zip-file fileb://http-request.zip
aws lambda update-function-code --function-name "redirect" --zip-file fileb://redirect.zip

API_ID=`aws apigateway get-rest-apis --query 'items[].id' --output yaml | cut -c 3-`
echo "Deploying API ($API_ID) stage..."
aws apigateway create-deployment --rest-api-id $API_ID --stage-name Prod

rm packaged.yml
rm redirect.zip
rm http-request.zip
rm serve-image.zip
echo "Finished cleanup."

```