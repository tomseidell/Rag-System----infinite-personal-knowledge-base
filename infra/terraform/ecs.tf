resource "aws_ecs_cluster" "main" { # cluster containing api, worker, and pdf-reader containers
  name = "main-cluster"
}


#   api config :

# plan for starting api container 
resource "aws_ecs_task_definition" "api" {

  # task level config
  family = "api-task" # task name
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn # iam role for ecs to pull images from ecr and to push logs to cloud watch
  task_role_arn      = aws_iam_role.ecs_task_role.arn # iam role for code inside the container (S3, etc.)
  network_mode = "awsvpc" # container receives dedicated ip from vpc
  requires_compatibilities = ["FARGATE"] # let aws validate task definition for fargate => when misconfig : throws error before starting
  # ressources for container
  cpu    = var.api_fargate_cpu
  memory = var.api_fargate_memory

  # container level config 
  container_definitions = templatefile("./templates/ecs/api.json.tpl", {
    api_image  = "${aws_ecr_repository.api.repository_url}:latest"
    aws_region = var.region
    api_port           = var.api_port
    db_user            = var.db_user
    db_name            = var.db_name
    db_host            = aws_db_instance.postgres.address
    environment        = var.environment
    db_password_arn    = "${aws_db_instance.postgres.master_user_secret[0].secret_arn}:password::"
    jwt_secret_arn     = "${aws_secretsmanager_secret.main.arn}:JWT_SECRET::"
    openai_key_arn     = "${aws_secretsmanager_secret.main.arn}:OPENAI_API_KEY::"
    qdrant_key_arn     = "${aws_secretsmanager_secret.main.arn}:QDRANT_API_KEY::"
    qdrant_url         = var.qdrant_url
    redis_url          = "redis://${aws_elasticache_cluster.main.cache_nodes[0].address}:${aws_elasticache_cluster.main.port}"
    s3_bucket_name     = aws_s3_bucket.main.id
  })
}

# manages starting of api container
resource "aws_ecs_service" "api" {
  name = "api-service" # service name
  cluster = aws_ecs_cluster.main.id # runs in main cluster
  task_definition = aws_ecs_task_definition.api.arn # which blue print / task definition to use
  desired_count = var.enable_services? var.api_count  : 0# number of container instances
  launch_type = "FARGATE" # start container as managed fargate instance

  # container run in private subnet with given network security
  network_configuration { 
    security_groups = [aws_security_group.api.id]
    subnets = aws_subnet.private.*.id
    assign_public_ip = false
  }

  # register container to load balancer
  load_balancer {
    target_group_arn = aws_alb_target_group.api.id
    container_name   = "api"
    container_port   = var.api_port
  }
}


#     worker config :

# plan for starting worker container
resource "aws_ecs_task_definition" "worker" {
  family = "worker-task"
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  cpu = var.worker_fargate_cpu
  memory = var.worker_fargate_memory

  container_definitions = templatefile("./templates/ecs/worker.json.tpl", {
    worker_image    = "${aws_ecr_repository.worker.repository_url}:latest"
    aws_region      = var.region
    db_user         = var.db_user
    db_name         = var.db_name
    db_host         = aws_db_instance.postgres.address
    environment     = var.environment
    db_password_arn = "${aws_db_instance.postgres.master_user_secret[0].secret_arn}:password::"
    jwt_secret_arn  = "${aws_secretsmanager_secret.main.arn}:JWT_SECRET::"
    openai_key_arn  = "${aws_secretsmanager_secret.main.arn}:OPENAI_API_KEY::"
    qdrant_key_arn  = "${aws_secretsmanager_secret.main.arn}:QDRANT_API_KEY::"
    qdrant_url      = var.qdrant_url
    redis_url       = "redis://${aws_elasticache_cluster.main.cache_nodes[0].address}:${aws_elasticache_cluster.main.port}"
    s3_bucket_name  = aws_s3_bucket.main.id
  })
}

# manages starting of worker container
resource "aws_ecs_service" "worker" {
  name = "worker-service"
  cluster = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count = var.enable_services? var.worker_count  : 0
  launch_type = "FARGATE"

  network_configuration {
    security_groups = [aws_security_group.worker.id]
    subnets = aws_subnet.private.*.id
    assign_public_ip = false
  }
}


# pdf-reader worker 

resource "aws_ecs_task_definition" "pdf_reader" {
  family                   = "pdf-reader-task"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  cpu    = var.pdf_reader_fargate_cpu
  memory = var.pdf_reader_fargate_memory

  container_definitions = templatefile("./templates/ecs/pdf_reader.json.tpl", {
    worker_image    = "${aws_ecr_repository.worker.repository_url}:latest"
    aws_region      = var.region
    db_user         = var.db_user
    db_name         = var.db_name
    db_host         = aws_db_instance.postgres.address
    environment     = var.environment
    db_password_arn = "${aws_db_instance.postgres.master_user_secret[0].secret_arn}:password::"
    jwt_secret_arn  = "${aws_secretsmanager_secret.main.arn}:JWT_SECRET::"
    redis_url       = "redis://${aws_elasticache_cluster.main.cache_nodes[0].address}:${aws_elasticache_cluster.main.port}"
    s3_bucket_name  = aws_s3_bucket.main.id
  })
}

resource "aws_ecs_service" "pdf_reader" {
  name            = "pdf-reader-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.pdf_reader.arn
  desired_count   = var.enable_services ? var.pdf_reader_count : 0
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.worker.id]
    subnets          = aws_subnet.private.*.id
    assign_public_ip = false
  }
}
