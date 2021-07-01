resource "aws_api_gateway_resource" "streams_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  parent_id   = aws_api_gateway_rest_api.api_gateway_rest_api.root_resource_id
  path_part   = "streams"
}



resource "aws_api_gateway_resource" "streams_motion_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  parent_id   = aws_api_gateway_resource.streams_resource.id
  path_part   = "motion"
}

resource "aws_api_gateway_method" "streams_motion_endpoint" {
  rest_api_id     = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id     = aws_api_gateway_resource.streams_motion_resource.id
  http_method     = "GET"
  authorization   = "NONE"
  operation_name  = "Serve motion asset by invoking lambda"
}

resource "aws_api_gateway_integration" "streams_motion_endpoint_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id             = aws_api_gateway_resource.streams_motion_resource.id
  http_method             = aws_api_gateway_method.streams_motion_endpoint.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.motion_events_lambda.invoke_arn
  credentials             = aws_iam_role.s3_static_resources_role.arn
}



resource "aws_api_gateway_resource" "streams_door_resource" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  parent_id   = aws_api_gateway_resource.streams_resource.id
  path_part   = "door"
}

resource "aws_api_gateway_method" "streams_door_endpoint" {
  rest_api_id     = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id     = aws_api_gateway_resource.streams_door_resource.id
  http_method     = "GET"
  authorization   = "NONE"
  operation_name  = "Invoke door stream"
}

resource "aws_api_gateway_integration" "streams_door_endpoint_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api_gateway_rest_api.id
  resource_id             = aws_api_gateway_resource.streams_door_resource.id
  http_method             = aws_api_gateway_method.streams_door_endpoint.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.redirect_lambda.invoke_arn
}
