resource "aws_lambda_function" "motion_events_lambda" {
  depends_on = [
    aws_lambda_layer_version.lambda_layer_sqs,
    aws_lambda_layer_version.lambda_layer_ssm,
    aws_lambda_layer_version.lambda_layer_pymysql
  ]
  function_name = "api_motion_events_lambda"
  filename = "../serve-motion.zip"
  handler = "serve-motion.lambda_handler"
  runtime = "python3.8"
  role = aws_iam_role.motion_events_lambda_role.arn
  layers = [
    aws_lambda_layer_version.lambda_layer_sqs.arn,
    aws_lambda_layer_version.lambda_layer_ssm.arn,
    aws_lambda_layer_version.lambda_layer_pymysql.arn
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

resource "aws_cloudwatch_log_group" "motion_events_lambda_logs" {
  name              = "/aws/lambda/api_motion_events_lambda"
  retention_in_days = 7
}

resource "aws_iam_role" "motion_events_lambda_role" {
  name = "motion_events_lambda_role"
  assume_role_policy = file("data/lambda_trust_relationship.json")
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    aws_iam_policy.motion_events_lambda_exec_policy.arn
  ]
}

resource "aws_iam_policy" "motion_events_lambda_exec_policy" {
  name = "motion_events_lambda_exec_policy"
  policy = templatefile("data/lambda_motion_events_exec_role.json", {
    ssm_resources = var.ssm_resources,
    sqs_resources = var.sqs_resources,
    s3_resources = var.motion_events_bucket
  })
}