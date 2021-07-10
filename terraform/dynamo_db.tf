resource "aws_dynamodb_table" "home_api_dynamo_db" {
  name           = var.dynamo_table_name
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "Principal"
  range_key      = "Timestamp"

  attribute {
    name = "Timestamp"
    type = "S"
  }

  attribute {
    name = "Principal"
    type = "S"
  }

}