resource "aws_api_gateway_resource" "static_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  parent_id   = aws_api_gateway_rest_api.api_gateway_rest_api.root_resource_id
  path_part   = "static"
}

resource "aws_api_gateway_resource" "static_proxy_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  parent_id   = aws_api_gateway_resource.static_resource.id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "static_proxy_endpoint" {
  rest_api_id     = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id     = aws_api_gateway_resource.static_proxy_resource.id
  http_method     = "GET"
  authorization   = "CUSTOM"
  authorizer_id   = aws_api_gateway_authorizer.api_gateway_lambda_authorizer.id
  operation_name  = "Static resource proxy endpoint"
  request_parameters = {
    "method.request.path.proxy" = true
  }
}

resource "aws_api_gateway_integration" "static_proxy_endpoint_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id             = aws_api_gateway_resource.static_proxy_resource.id
  http_method             = aws_api_gateway_method.static_proxy_endpoint.http_method
  type                    = "AWS"
  integration_http_method = "GET"
  uri                     = "arn:aws:apigateway:us-east-1:s3:path/${var.resource_bucket}/{proxy}"
  credentials             = aws_iam_role.s3_static_resources_role.arn
  request_parameters = {
    "integration.request.path.proxy" = "method.request.path.proxy"
  }
}

resource "aws_api_gateway_method_response" "static_proxy_endpoint_method_response" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id = aws_api_gateway_resource.static_proxy_resource.id
  http_method = aws_api_gateway_method.static_proxy_endpoint.http_method
  status_code = "200"
  response_models = {
    "text/html" = "Empty"
    "image/png" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "static_proxy_endpoint_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id = aws_api_gateway_resource.static_proxy_resource.id
  http_method = aws_api_gateway_method.static_proxy_endpoint.http_method
  status_code = aws_api_gateway_method_response.static_proxy_endpoint_method_response.status_code
  response_templates = {
    "text/html" = "",
    "image/png" = ""
  }
}
