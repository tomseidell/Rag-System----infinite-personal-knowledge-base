[
  {
    "name": "worker",
    "image": "${worker_image}",
    "cpu": ${worker_fargate_cpu},
    "memory": ${worker_fargate_memory},
    "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/worker",
          "awslogs-region": "${aws_region}",
          "awslogs-stream-prefix": "ecs"
        }
    },
    "portMappings": []
  }
]