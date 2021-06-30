resource "aws_api_gateway_method" "root_endpoint" {
  rest_api_id     = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id     = aws_api_gateway_rest_api.api_gateway_rest_api.root_resource_id
  http_method     = "GET"
  authorization   = "NONE"
  operation_name  = "Root endpoint"
}

resource "aws_api_gateway_integration" "root_endpoint_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id             = aws_api_gateway_rest_api.api_gateway_rest_api.root_resource_id
  http_method             = aws_api_gateway_method.root_endpoint.http_method
  type                    = "AWS"
  integration_http_method = "GET"
  uri                     = var.rootEndpointUri
  credentials             = aws_iam_role.s3_static_resources_role.arn
  request_templates = {
    "text/html" = "#set($allParams = $input.params()){\"body-json\" : $input.json('$'),\"headers\": {\"key-header\" : \"$util.escapeJavaScript($context.authorizer.key)\", #foreach($param in $input.params().header.keySet()) \"$param\": \"$util.escapeJavaScript($input.params().header.get($param))\" #if($foreach.hasNext),#end #end } }"
  }
  passthrough_behavior    = "WHEN_NO_MATCH"
}

resource "aws_api_gateway_method_response" "root_endpoint_integration_method_response" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id = aws_api_gateway_rest_api.api_gateway_rest_api.root_resource_id
  http_method = aws_api_gateway_method.root_endpoint.http_method
  status_code = "200"
  response_models = {
    "text/html" = "Empty"
  }
  response_parameters = {
    "method.response.header.principalId" = true
  }
}

resource "aws_api_gateway_integration_response" "root_endpoint_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id = aws_api_gateway_rest_api.api_gateway_rest_api.root_resource_id
  http_method = aws_api_gateway_method.root_endpoint.http_method
  status_code = aws_api_gateway_method_response.root_endpoint_integration_method_response.status_code

  response_parameters = {
    "method.response.header.principalId" = "context.authorizer.principalId"
  }
}

resource "aws_iam_role" "s3_static_resources_role" {
  name = "s3_static_resources_role"
  assume_role_policy = file("data/api_gateway_trust_relationship.json")
  managed_policy_arns = [
    aws_iam_policy.s3_static_resources_policy.arn,
  ]
}

resource "aws_iam_policy" "s3_static_resources_policy" {
  name = "s3_static_resources_policy"
  policy = templatefile("data/s3_static_resources_role.json", {
    s3_resources = var.s3_resources
  })
}