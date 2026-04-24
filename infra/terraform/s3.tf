resource "aws_s3_bucket" "main" {
  bucket = "${var.project_name}-main-${var.environment}"
  force_destroy = true # allows to shut down even with items inside
}

resource "aws_s3_bucket_public_access_block" "shared" {
  bucket = aws_s3_bucket.main.id # connect to bucket

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
