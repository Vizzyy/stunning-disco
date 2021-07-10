resource "aws_lambda_function" "authorizer_lambda" {
  function_name = "api_authorizer_lambda"
  filename = "../authorizer.zip"
  handler = "authorizer.lambda_handler"
  runtime = "python3.8"
  role = aws_iam_role.redirect_lambda_role.arn
  environment {
    variables = {
      TableName = var.dynamo_table_name
      TZ = "America/New_York"
    }
  }
  timeout = 30
  memory_size = 128
}

resource "aws_cloudwatch_log_group" "authorizer_lambda_logs" {
  name              = "/aws/lambda/authorizer_lambda"
  retention_in_days = 7
}

resource "aws_iam_role" "authorizer_lambda_role" {
  name = "authorizer_lambda_role"
  assume_role_policy = file("data/lambda_trust_relationship.json")
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
}
