terraform {
  backend "s3" {
    bucket         = "tfstate-682405977183-eu-central-1"
    key            = "cb/dev/terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
