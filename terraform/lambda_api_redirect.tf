data "archive_file" "api_redirect_lambda_zip" {
  type = "zip"
  source_file = "../lambdas/api_redirect_lambda.py"
  output_path = "../build/api_redirect_lambda.zip"
}

resource "aws_lambda_function" "redirect_lambda" {
  function_name = "api_redirect_lambda"
  filename = data.archive_file.api_redirect_lambda_zip.output_path
  source_code_hash = data.archive_file.api_redirect_lambda_zip.output_base64sha256
  handler = "api_redirect_lambda.lambda_handler"
  runtime = "python3.8"
  role = aws_iam_role.redirect_lambda_role.arn
  environment {
    variables = {
      REDIRECT_URL = var.door_stream_path
      TZ = "America/New_York"
    }
  }
  timeout = 30
  memory_size = 128
}

resource "aws_cloudwatch_log_group" "redirect_lambda_logs" {
  name              = "/aws/lambda/api_redirect_lambda"
  retention_in_days = 7
}

resource "aws_iam_role" "redirect_lambda_role" {
  name = "redirect_lambda_role"
  assume_role_policy = file("data/lambda_trust_relationship.json")
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
}
