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
    "portMappings": [],
    "environment": [
      { "name": "DATABASE_PORT", "value": "5432" },
      { "name": "DATABASE_USER", "value": "${db_user}" },
      { "name": "DATABASE_NAME", "value": "${db_name}" },
      { "name": "DATABASE_HOST", "value": "${db_host}" },
      { "name": "ENVIRONMENT", "value": "${environment}" },
      { "name": "DENSE_VECTOR_SIZE", "value": "768" }
      { "name": "QDRANT_URL", "value": "${qdrant_url}" }
      { "name": "CELERY_BROKER_URL", "value": "${redis_url}" },
      { "name": "CELERY_RESULT_BACKEND", "value": "${redis_url}" },
      { "name": "REDIS_URL", "value": "${redis_url}" },
      { "name": "S3_BUCKET_NAME", "value": "${s3_bucket_name}" }



    ],
    "secrets": [
      { "name": "DATABASE_PASSWORD", "valueFrom": "${db_password_arn}" },
      { "name": "OPENAI_API_KEY", "valueFrom": "${openai_key_arn}" },
      { "name": "QDRANT_API_KEY", "valueFrom": "${qdrant_key_arn}" }
    ]
  }
]
