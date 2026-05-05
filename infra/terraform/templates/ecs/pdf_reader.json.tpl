[
  {
    "name": "pdf-reader",
    "image": "${worker_image}",
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/pdf-reader",
        "awslogs-region": "${aws_region}",
        "awslogs-stream-prefix": "ecs"
      }
    },
    "portMappings": [],
    "environment": [
      { "name": "DATABASE_PORT", "value": "5432" },
      { "name": "DATABASE_USER", "value": "${db_user}" },
      { "name": "DB_NAME", "value": "${db_name}" },
      { "name": "DB_HOST", "value": "${db_host}" },
      { "name": "ENVIRONMENT", "value": "${environment}" },
      { "name": "CELERY_BROKER_URL", "value": "${redis_url}" },
      { "name": "CELERY_RESULT_BACKEND", "value": "${redis_url}" },
      { "name": "REDIS_URL", "value": "${redis_url}" },
      { "name": "WORKER_TYPE", "value": "pdf_reader" },
      { "name": "S3_BUCKET_NAME", "value": "${s3_bucket_name}" }
    ],
    "secrets": [
      { "name": "DATABASE_PASSWORD", "valueFrom": "${db_password_arn}" },
      { "name": "JWT_SECRET", "valueFrom": "${jwt_secret_arn}" }
    ]
  }
]
