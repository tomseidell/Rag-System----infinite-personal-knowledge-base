output "api_ecr_url" {
  value = aws_ecr_repository.api.repository_url
}

output "worker_ecr_url" {
  value = aws_ecr_repository.worker.repository_url
}