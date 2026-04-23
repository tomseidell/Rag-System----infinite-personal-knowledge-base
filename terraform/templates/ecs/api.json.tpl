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
    ],
    "environment": [
      { "name": "DATABASE_PORT", "value": "5432" },
      { "name": "DATABASE_USER", "value": "${db_user}" },
      { "name": "DATABASE_NAME", "value": "${db_name}" },
      { "name": "DATABASE_HOST", "value": "${db_host}" },
      { "name": "ENVIRONMENT", "value": "${environment}" },
      { "name": "ALGORITHM", "value": "HS256" },
      { "name": "ACCESS_TOKEN_EXPIRE_MINUTES", "value": "30" },
      { "name": "REFRESH_TOKEN_EXPIRE_DAYS", "value": "30" },
      { "name": "DENSE_VECTOR_SIZE", "value": "768" }
    ],
    "secrets": [
      { "name": "DATABASE_PASSWORD", "valueFrom": "${db_password_arn}" },
      { "name": "JWT_SECRET", "valueFrom": "${jwt_secret_arn}" },
      { "name": "OPENAI_API_KEY", "valueFrom": "${openai_key_arn}" },
      { "name": "QDRANT_API_KEY", "valueFrom": "${qdrant_key_arn}" }
    ]
  }
]
