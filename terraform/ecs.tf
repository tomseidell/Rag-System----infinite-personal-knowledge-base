resource "aws_ecs_cluster" "main" { # cluster containing api and worker container
  name = "main-cluster"
}


#   api config :

# reads external api template file and fills it with vars
data "template_file" "api" { 
  template = file("./templates/ecs/api.json.tpl") # route to api template file

  # template contains container definition for api container

  vars = {
    api_image = var.api_image
    api_port = var.api_port
    api_fargate_cpu = var.api_fargate_cpu
    api_fargate_memory = var.api_fargate_memory


    aws_region = var.region
  }
}

# plan for starting api container 
resource "aws_ecs_task_definition" "api" {
  family = "api-task" # task name 
  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn # iam role for ecs to pull images from ecr and to push logs to cloud watch
  network_mode = "awsvpc" # container receives dedicated ip from vpc
  requires_compatibilities = ["Fargate"] # let aws validate task definition for fargate => when misconfig : throws error before starting

  # ressources for container
  cpu = var.api_fargate_cpu
  memory = var.api_memory

  # container definitions / config from external template file
  container_definitions = data.template_file.api.rendered
}

# manages starting of api container
resource "aws_ecs_service" "api" {
  name = "api-service" # service name
  cluster = aws_ecs_cluster.main.id # runs in main cluster
  task_definition = aws_ecs_task_definition.api.arn # which blue print / task definition to use
  desired_count = var.api_count # number of container instances
  launch_type = "Fargate" # start container as managed fargate instance


  # container run in private subnet with given network security
  network_configuration { 
    security_groups = [aws_security_group.api.id]
    subnets = aws_subnet.private.*.id
    assign_public_ip = false
  }

  # register container to load balancer
  load_balancer {
    target_group_arn = aws_alb_target_group.app.id
    container_name   = "api"
    container_port   = var.api_port
  }
}



#     worker config :

#reads external worker template file and fills it with vars
data "template_file" "worker" { 
  template = file("./templates/ecs/worker.json.tpl") # route to worker template file

  # template contains container definition for worker container

  vars = {

    worker_image          = var.worker_image
    worker_fargate_cpu    = var.worker_fargate_cpu
    worker_fargate_memory = var.worker_fargate_memory

    aws_region = var.region
  }
} 

resource "aws_ecs_task_definition" "worker" {
    family = "worker-task"
    execution_role_arn = aws_iam_role.ecs_task_execution_role.arn
    network_mode = "awsvpc"
    requires_compatibilities = ["Fargate"]

    cpu = var.worker_fargate_cpu
    memory = var.worker_fargate_memory

    container_definitions = data.template_file.worker.rendered
}

resource "aws_ecs_service" "worker" {
  name = "worker-service"
  cluster = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count = var.worker_count
  launch_type = "Fargate"

  network_configuration { 
    security_groups = [aws_security_group.worker.id]
    subnets = aws_subnet.private.*.id
    assign_public_ip = false
  }

}