resource "aws_api_gateway_rest_api" "api_gateway_rest_api" {
  name = var.restApiName
  disable_execute_api_endpoint = true
  binary_media_types = ["*/*"]

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_deployment" "api_gateway_deployement" {
  depends_on = [
    aws_api_gateway_method.api_proxy_endpoint,
    aws_api_gateway_method.root_endpoint,
    aws_api_gateway_method.logs_endpoint,
    aws_api_gateway_method.static_proxy_endpoint,
    aws_api_gateway_integration.api_proxy_endpoint_integration,
    aws_api_gateway_integration.logs_endpoint_integration,
    aws_api_gateway_integration.root_endpoint_integration,
    aws_api_gateway_integration.static_proxy_endpoint_integration,
    aws_api_gateway_integration.streams_door_endpoint_integration,
    aws_api_gateway_integration.streams_motion_endpoint_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "api_gateway_stage" {
  depends_on = [aws_cloudwatch_log_group.api_gateway_rest_api_log_group]
  deployment_id = aws_api_gateway_deployment.api_gateway_deployement.id
  rest_api_id   = aws_api_gateway_rest_api.api_gateway_rest_api.id
  stage_name    = "Prod"
}

resource "aws_cloudwatch_log_group" "api_gateway_rest_api_log_group" {
  name = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.api_gateway_rest_api.id}/Prod"
  retention_in_days = 7
}

resource "aws_api_gateway_method_settings" "all" {
  rest_api_id = aws_api_gateway_rest_api.api_gateway_rest_api.id
  stage_name  = aws_api_gateway_stage.api_gateway_stage.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = false // Detailed CloudWatch Metrics (Costs extra)
    data_trace_enabled = true
    throttling_burst_limit = 10
    throttling_rate_limit = 10
    logging_level   = "INFO"
  }
}

resource "aws_api_gateway_domain_name" "api_gateway_domain_name" {
  domain_name               = var.domainName
  regional_certificate_arn  = var.apiHostCert
  security_policy           = "TLS_1_2"

  mutual_tls_authentication {
    truststore_uri = var.trustStoreUri
  }
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_base_path_mapping" "api_gateway_base_path_mapping" {
  api_id      = aws_api_gateway_rest_api.api_gateway_rest_api.id
  stage_name  = aws_api_gateway_stage.api_gateway_stage.stage_name
  domain_name = aws_api_gateway_domain_name.api_gateway_domain_name.domain_name
}

resource "aws_route53_record" "route53_record" {
  name    = var.domainName
  type    = "A"
  zone_id = var.hostedZoneId

  alias {
    evaluate_target_health = false
    name                   = aws_api_gateway_domain_name.api_gateway_domain_name.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.api_gateway_domain_name.regional_zone_id
  }
}

resource "aws_iam_role" "api_gateway_lambda_integrations" {
  name = "api_gateway_lambda_integrations"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      },
    ]
  })

  managed_policy_arns = [aws_iam_policy.api_gateway_lambda_integrations_policy.arn]
}

resource "aws_iam_policy" "api_gateway_lambda_integrations_policy" {
  name = "api_gateway_lambda_integrations_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["lambda:InvokeFunction"]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

resource "aws_api_gateway_authorizer" "api_gateway_lambda_authorizer" {
  name                   = "api_gateway_lambda_authorizer"
  rest_api_id            = aws_api_gateway_rest_api.api_gateway_rest_api.id
  authorizer_uri         = aws_lambda_function.api_authorizer_lambda.invoke_arn
  authorizer_credentials = aws_iam_role.api_authorizer_lambda_role.arn
  type = "REQUEST"
  authorizer_result_ttl_in_seconds = 0
  identity_source = ""
}