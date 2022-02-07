resource "aws_lambda_function" "api_proxy_lambda" {
  depends_on = [
    aws_lambda_layer_version.lambda_layer_sqs,
    aws_lambda_layer_version.lambda_layer_ssm
  ]
  function_name = "api_proxy_lambda"
  s3_bucket = var.lambda_layers_bucket
  s3_key = "api_proxy_lambda.zip"
  source_code_hash = filebase64sha256("../build/api_proxy_lambda.zip")
  handler = "api_proxy_lambda.lambda_handler"
  runtime = "python3.8"
  role = aws_iam_role.api_proxy_lambda_role.arn
  layers = [
    aws_lambda_layer_version.lambda_layer_sqs.arn,
    aws_lambda_layer_version.lambda_layer_ssm.arn
  ]
  environment {
    variables = {
      SSM_PATH = var.ssm_path
      TZ = "America/New_York"
    }
  }
  timeout = 30
  memory_size = 128
}

resource "aws_cloudwatch_log_group" "api_proxy_lambda_logs" {
  name              = "/aws/lambda/api_proxy_lambda"
  retention_in_days = 7
}

resource "aws_iam_role" "api_proxy_lambda_role" {
  name = "api_proxy_lambda_role"
  assume_role_policy = file("data/lambda_trust_relationship.json")
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    aws_iam_policy.api_proxy_lambda_exec_policy.arn
  ]
}

resource "aws_iam_policy" "api_proxy_lambda_exec_policy" {
  name = "api_proxy_lambda_exec_policy"
  policy = templatefile("data/lambda_api_proxy_exec_role.json", {
    ssm_resources = var.ssm_resources,
    sqs_resources = var.sqs_resources
  })
}
