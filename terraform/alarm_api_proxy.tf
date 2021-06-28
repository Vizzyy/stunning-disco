resource "aws_cloudwatch_metric_alarm" "api_proxy_lambda_alarm" {
  alarm_name                = "api_proxy_lambda_alarm"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  datapoints_to_alarm       = "1" # this is the M in "M out of N data points to alarm"
  evaluation_periods        = "5" # this is the N in "M out of N data points to alarm"
  metric_name               = "Errors"
  namespace                 = "AWS/Lambda"
  period                    = "60" # seconds between data points
  statistic                 = "Sum"
  threshold                 = "2"
  alarm_description         = "Alarm if 1 bad data point (of >= 2 errors each) within 5 mins"
  treat_missing_data        = "notBreaching"

  dimensions                = {
    name = "FunctionName"
    value = aws_lambda_function.api_proxy_lambda.function_name
  }
}