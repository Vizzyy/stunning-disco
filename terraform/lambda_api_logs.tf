resource "aws_lambda_function" "api_logs_lambda" {
  function_name = "api_logs_lambda"
  filename = "../api-logs.zip"
  handler = "api-logs.lambda_handler"
  runtime = "python3.8"
  role = aws_iam_role.api_logs_lambda_role.arn
  environment {
    variables = {
      TableName = aws_dynamodb_table.home_api_dynamo_db.name
      TZ = "America/New_York"
    }
  }
}

resource "aws_cloudwatch_log_group" "api_logs_lambda_logs" {
  name              = "/aws/lambda/api_logs_lambda"
  retention_in_days = 7
}

resource "aws_iam_role" "api_logs_lambda_role" {
  name = "api_logs_lambda_role"
  assume_role_policy = file("data/lambda_trust_relationship.json")
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    aws_iam_policy.api_logs_lambda_exec_policy.arn
  ]
}

resource "aws_iam_policy" "api_logs_lambda_exec_policy" {
  name = "api_logs_lambda_exec_policy"
  policy = templatefile("data/lambda_api_logs_exec_role.json", {
    ddb_resources = aws_dynamodb_table.home_api_dynamo_db.arn
  })
}