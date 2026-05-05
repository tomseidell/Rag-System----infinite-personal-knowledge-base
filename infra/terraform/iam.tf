resource "aws_iam_policy" "s3_access" {
  name = "s3-access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ]
      Resource = [
        aws_s3_bucket.main.arn,          # für ListBucket
        "${aws_s3_bucket.main.arn}/*"    # für Get/Put/Delete auf Objekte
      ]
    }]
  })
}


resource "aws_iam_policy" "secrets_access" {
  name = "secrets-access"

  # policy = scope of the iam role
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [
        aws_db_instance.postgres.master_user_secret[0].secret_arn, # created by aws during db creation
        aws_secretsmanager_secret.main.arn # api keys, manually createt sm
      ]
    }]
  })
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs-task-execution-role"

  # assume_role_policy = who is allowed to apply this iam role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_task_execution_role.name # who is allowed to use

  # use aws managed policy to allow ecs to pull from ecr and create logs 
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy" # what is allowed to be done
}

resource "aws_iam_role_policy_attachment" "ecs_secrets" {
  role       = aws_iam_role.ecs_task_execution_role.name # who is allowed to use

  # use self created policy from above
  policy_arn = aws_iam_policy.secrets_access.arn # what is allowed to be done
}

resource "aws_iam_role" "ecs_task_role" {
  name = "ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_s3" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.s3_access.arn
}
