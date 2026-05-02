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
      { "name": "DB_NAME", "value": "${db_name}" },
      { "name": "DB_HOST", "value": "${db_host}" },
      { "name": "ENVIRONMENT", "value": "${environment}" },
      { "name": "ALGORITHM", "value": "HS256" },
      { "name": "ACCESS_TOKEN_EXPIRE_MINUTES", "value": "30" },
      { "name": "REFRESH_TOKEN_EXPIRE_DAYS", "value": "30" },
      { "name": "DENSE_VECTOR_SIZE", "value": "768" },
      { "name": "QDRANT_URL", "value": "${qdrant_url}" },
      { "name": "CELERY_BROKER_URL", "value": "${redis_url}" },
      { "name": "CELERY_RESULT_BACKEND", "value": "${redis_url}" },
      { "name": "REDIS_URL", "value": "${redis_url}" },
      { "name": "S3_BUCKET_NAME", "value": "${s3_bucket_name}" }




    ],
    "secrets": [
      { "name": "DATABASE_PASSWORD", "valueFrom": "${db_password_arn}" },
      { "name": "JWT_SECRET", "valueFrom": "${jwt_secret_arn}" },
      { "name": "OPENAI_API_KEY", "valueFrom": "${openai_key_arn}" },
      { "name": "QDRANT_API_KEY", "valueFrom": "${qdrant_key_arn}" }
    ]
  }
]
