resource "aws_s3_bucket_object" "static_web_resources" {
  for_each = fileset("../static", "*")

  bucket = var.resource_bucket
  key    = each.value
  source = "../static/${each.value}"
  etag   = filemd5("../static/${each.value}")
}
