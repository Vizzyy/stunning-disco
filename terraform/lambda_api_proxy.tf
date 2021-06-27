resource "aws_lambda_function" "api_proxy_lambda" {
  function_name = "api_proxy_lambda"
  filename = "../http-request.zip"
  handler = "http-request.lambda_handler"
  runtime = "python3.8"
  role = aws_iam_role.api_proxy_lambda_role.arn
}

resource "aws_cloudwatch_log_group" "api_proxy_lambda_logs" {
  name              = "/aws/lambda/home/api_proxy_lambda"
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

data "template_file" "api_proxy_lambda_exec_policy_template" {
  template = file("data/lambda_api_proxy_exec_role.json.tpl")
  vars = {
    ssm_resources = var.ssm_resources,
    sqs_resources = var.sqs_resources
  }
}

resource "aws_iam_policy" "api_proxy_lambda_exec_policy" {
  name = "api_proxy_lambda_exec_policy"
  policy = data.template_file.api_proxy_lambda_exec_policy_template.rendered
}