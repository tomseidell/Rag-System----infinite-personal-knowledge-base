output "api_ecr_url" {
  value = aws_ecr_repository.api.repository_url
}

output "worker_ecr_url" {
  value = aws_ecr_repository.worker.repository_url
}

output "alb_hostname" {
  value = "${aws_alb.main.dns_name}:8000"
}


output "db_endpoint" {
  value = aws_db_instance.postgres.endpoint
}

output "db_secret_arn" {
  value = aws_db_instance.postgres.master_user_secret[0].secret_arn
}