variable "region" {
    description = "This is the cloud hosting region where the architecture is going to be deployed"
}

variable "health_check_path" {
  default = "/health"
}



# fargate api
variable "api_port" {
  description = "port where fargate api instance will run"
  default = 8000
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


# app image url, gets dynamically defined in cd pipeline
variable "api_image" {
    description = "Docker image URI from ECR"
}

# worker image url, gets dynamically defined in cd pipeline
variable "worker_image" {
    description = "Docker image URI from ECR"
}


variable "api_fargate_cpu" {
    default = "1024"
}
variable "api_fargate_memory" {
    default = "2048"
}

variable "worker_fargate_cpu" {
    default = "512"   
}
variable "worker_fargate_memory" {
    default = "2048"  
}



variable "api_count" {
  description = "numer of instances"
  default = 1
}

variable "worker_count" {
  description = "numer of instances"
  default = 2
}

variable "project_name"{
  default = "second-brain"
}


# database specific

variable "db_user" {
  description = "name of the db user"
}

variable "db_name"{
    description = "name of the database"
}


# secrets and envs

variable "openai_api_key" {
  description = "api key of openai"
}

variable "qdrant_api_key" {
  description = "api key of qdrant"
}

variable "environment" {
  description = "Deployment environment (e.g. dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "qdrant_url" {
  type        = string
  description = "Qdrant Cloud URL"
}



# config for initial apply
variable "enable_services" {
  type    = bool
  default = true
}