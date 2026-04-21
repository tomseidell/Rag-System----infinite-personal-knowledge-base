resource "aws_cloudwatch_log_group" "api_log_group" {
    name = "/ecs/api"
    retention_in_days = 5 
}
resource "aws_cloudwatch_log_stream" "api_log_stream" {
    name = "api-log-stream"
    log_group_name = aws_cloudwatch_log_group.api_log_group.name
}


resource "aws_cloudwatch_log_group" "worker_log_group" {
    name = "/ecs/worker"
    retention_in_days = 5
}
resource "aws_cloudwatch_log_stream" "worker_log_stream" {
    name = "worker-log-stream"
    log_group_name = aws_cloudwatch_log_group.worker_log_group.name
}
