[
  {
    "name": "api",
    "image": "${api_image}",
    "cpu": ${api_fargate_cpu},
    "memory": ${api_fargate_memory},
    "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/api",
          "awslogs-region": "${aws_region}",
          "awslogs-stream-prefix": "ecs"
        }
    },
    "portMappings": [
      {
        "containerPort": ${api_port},
        "hostPort": ${api_port}
      }
    ]
  }
]