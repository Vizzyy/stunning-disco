resource "aws_api_gateway_resource" "api_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  parent_id   = aws_api_gateway_rest_api.api_gateway_rest_api.root_resource_id
  path_part   = "api"
}

resource "aws_api_gateway_resource" "api_proxy_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  parent_id   = aws_api_gateway_resource.api_resource.id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "api_proxy_endpoint" {
  rest_api_id     = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id     = aws_api_gateway_resource.api_proxy_resource.id
  http_method     = "ANY"
  authorization   = "CUSTOM"
  authorizer_id   = aws_api_gateway_authorizer.api_gateway_lambda_authorizer.id
  operation_name  = "API proxy endpoint"
}

resource "aws_api_gateway_integration" "api_proxy_endpoint_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id             = aws_api_gateway_resource.api_proxy_resource.id
  http_method             = aws_api_gateway_method.api_proxy_endpoint.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.api_proxy_lambda.invoke_arn
  credentials             = aws_iam_role.api_gateway_lambda_integrations.arn
}
