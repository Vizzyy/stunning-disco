resource "aws_lambda_function" "api_authorizer_lambda" {
  function_name = "api_authorizer_lambda"
  filename = "../authorizer.zip"
  handler = "authorizer.lambda_handler"
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
    aws_iam_policy.api_authorizer_lambda_exec_policy.arn
  ]
}

resource "aws_iam_policy" "api_authorizer_lambda_exec_policy" {
  name = "api_authorizer_lambda_exec_policy"
  policy = templatefile("data/lambda_api_authorizer_exec_role.json", {
//    ssm_resources = var.ssm_resources,
//    sqs_resources = var.sqs_resources
  })
}