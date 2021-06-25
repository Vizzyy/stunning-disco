resource "aws_lambda_function" "example" {
  function_name = "api_proxy_lambda"
  filename = "../http-request.zip"
  handler = "http-request.lambda_handler"
  runtime = "python3.8"
  role = aws_iam_role.iam_for_lambda.arn

  depends_on = [
    aws_iam_role_policy_attachment.lambda_logs,
    aws_cloudwatch_log_group.example,
  ]
}

//resource "aws_iam_role" "lambda_exec" {
//  name = "api_proxy_lambda_exec_role"
//  assume_role_policy = file("data/api_proxy_lambda_exec_role.json")
//}

resource "aws_cloudwatch_log_group" "example" {
  name              = "/aws/lambda/api_proxy_lambda"
  retention_in_days = 14
}

# See also the following AWS managed policy: AWSLambdaBasicExecutionRole
resource "aws_iam_policy" "lambda_logging" {
  name        = "lambda_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    },
    {
      "Action": [
        "ssm:GetParametersByPath"
      ],
      "Effect": "Allow",
      "Resource": "${var.ssm_resources}"
    },
    {
      "Action": [
        "sqs:SendMessage"
      ],
      "Effect": "Allow",
      "Resource": "${var.sqs_resources}"
    }
  ]
}
EOF
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"
  assume_role_policy = file("data/api_proxy_lambda_exec_role.json")
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.iam_for_lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}