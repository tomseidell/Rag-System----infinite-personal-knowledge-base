terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "~> 5.92"
    }
  }
  required_version = ">=1.2"
}

provider "aws" {
  profile = "admin"
  region  = "eu-central-1"
}

resource "aws_s3_bucket" "tfstate" {
  bucket = "tfstate-682405977183-eu-central-1"
}

resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

output "tfstate_bucket" {
  value = aws_s3_bucket.tfstate.bucket
}

output "lock_table" {
  value = aws_dynamodb_table.locks.name
}
