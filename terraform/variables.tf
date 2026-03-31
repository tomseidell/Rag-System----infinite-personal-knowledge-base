variable "region" {
    description = "This is the cloud hosting region where the architecture is going to be deployed"
}

variable "health_check_path" {
  default = "/health"
}



# fargate api
variable "api_port" {
  description = "port where fargate api instance will run"
}
variable "api_health_check_path" {
  description = "path to health endpoint"
}
variable "api_cpu" {
  description = "amount of cpu fargate api requires"
}
variable "api_memory" {
  description = "amount of ram fargate api requires"
}

# network
variable "az_count" {
    description = "Number of Availability Zones to cover in a given region"
}


variable "worker_port"{
    description = "port where fargate worker instance will run"
}

variable "redis_port"{
    description = "port where redis / elasticache will run"
}