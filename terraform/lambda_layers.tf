resource "aws_lambda_layer_version" "lambda_layer_pymysql" {
  layer_name = "lambda_layer_pymysql"
  s3_bucket = var.lambda_layers_bucket
  s3_key = var.lambda_layer_pymysql_artifact
  compatible_runtimes = ["python3.8"]
}

resource "aws_lambda_layer_version" "lambda_layer_sqs" {
  layer_name = "lambda_layer_sqs"
  s3_bucket = var.lambda_layers_bucket
  s3_key = var.lambda_layer_sqs_artifact
  compatible_runtimes = ["python3.8"]
}

resource "aws_lambda_layer_version" "lambda_layer_ssm" {
  layer_name = "lambda_layer_ssm"
  s3_bucket = var.lambda_layers_bucket
  s3_key = var.lambda_layer_ssm_artifact
  compatible_runtimes = ["python3.8"]
}