resource "aws_api_gateway_resource" "logs_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  parent_id   = aws_api_gateway_resource.api_resource.id
  path_part   = "logs"
}

resource "aws_api_gateway_method" "logs_endpoint" {
  rest_api_id     = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id     = aws_api_gateway_resource.logs_resource.id
  http_method     = "GET"
  authorization   = "CUSTOM"
  authorizer_id   = aws_api_gateway_authorizer.api_gateway_lambda_authorizer.id
  operation_name  = "API logs endpoint"
}

resource "aws_api_gateway_integration" "logs_endpoint_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id             = aws_api_gateway_resource.logs_resource.id
  http_method             = aws_api_gateway_method.logs_endpoint.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.api_logs_lambda.invoke_arn
  credentials             = aws_iam_role.api_gateway_lambda_integrations.arn
}
