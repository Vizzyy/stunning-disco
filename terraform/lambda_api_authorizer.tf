data "archive_file" "api_authorizer_lambda_zip" {
  type = "zip"
  source_file = "../lambdas/api_authorizer_lambda.py"
  output_path = "../build/api_authorizer_lambda.zip"
}

resource "aws_lambda_function" "api_authorizer_lambda" {
  function_name = "api_authorizer_lambda"
  filename = data.archive_file.api_authorizer_lambda_zip.output_path
  source_code_hash = data.archive_file.api_authorizer_lambda_zip.output_base64sha256
  handler = "api_authorizer_lambda.lambda_handler"
  runtime = "python3.8"
  role = aws_iam_role.api_authorizer_lambda_role.arn
  environment {
    variables = {
      TableName = var.dynamo_table_name
      TZ = "America/New_York"
    }
  }
  timeout = 30
  memory_size = 128
}

resource "aws_cloudwatch_log_group" "api_authorizer_lambda_logs" {
  name              = "/aws/lambda/api_authorizer_lambda"
  retention_in_days = 7
}

resource "aws_iam_role" "api_authorizer_lambda_role" {
  name = "api_authorizer_lambda_role"
  assume_role_policy = file("data/authorizer_trust_relationship.json")
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    aws_iam_policy.api_gateway_lambda_integrations_policy.arn,
    aws_iam_policy.api_logs_lambda_exec_policy.arn
  ]
}
