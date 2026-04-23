resource "aws_secretsmanager_secret" "main" {
  name = "main_secret_manager"
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}


resource "aws_secretsmanager_secret_version" "main" {
  secret_id = aws_secretsmanager_secret.main.id
  secret_string = jsonencode({
    OPENAI_API_KEY = var.openai_api_key
    QDRANT_API_KEY = var.qdrant_api_key
    JWT_SECRET = random_password.jwt_secret
  })
}