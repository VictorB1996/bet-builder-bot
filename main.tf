terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_ecr_repository" "aws_ecr_repository" {
  name                 = var.aws_ecr_repository_name
  image_tag_mutability = "MUTABLE"
  tags = {
    Name        = var.aws_ecr_repository_name
    Environment = "dev"
  }
}

resource "aws_lambda_function" "aws_lambda_function" {
  function_name = var.aws_lambda_function_name
  role          = aws_iam_role.aws_lambda_role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.aws_ecr_repository.repository_url}:latest"
  timeout       = 900
  memory_size   = 1024
  image_config {
    command     = ["main.lambda_handler"]
    entry_point = ["/var/runtime/bootstrap"]
  }
}

resource "aws_iam_role" "aws_lambda_role" {
  name = "${var.aws_lambda_function_name}-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      },
      {
        Effect = "Allow",
        Principal = {
          Service = "scheduler.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_secrets_policy" {
  name = "${var.aws_lambda_function_name}-secrets-access"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "secretsmanager:GetSecretValue"
        ],
        Resource = [
          for secret in aws_secretsmanager_secret.aws_secrets : secret.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_secrets_policy" {
  role       = aws_iam_role.aws_lambda_role.name
  policy_arn = aws_iam_policy.lambda_secrets_policy.arn
}

resource "aws_iam_role_policy" "custom_lambda_policy" {
  name = "custom_lambda_policy"
  role = aws_iam_role.aws_lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "lambda:InvokeFunction",
          "lambda:GetFunction",
          "scheduler:GetSchedule",
          "scheduler:CreateSchedule",
          "scheduler:DeleteSchedule",
          "iam:PassRole"
        ],
        Resource = [
          "arn:aws:lambda:${var.aws_region}:${var.aws_account_id}:function:${var.aws_lambda_function_name}:*",
          "arn:aws:lambda:${var.aws_region}:${var.aws_account_id}:function:${var.aws_lambda_function_name}",
          "arn:aws:scheduler:${var.aws_region}:${var.aws_account_id}:schedule/default/*",
          "arn:aws:iam::${var.aws_account_id}:role/${var.aws_lambda_function_name}-role"
        ]
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "aws_lambda_policy_attachment" {
  name       = "${var.aws_lambda_function_name}-policy-attachment"
  roles      = [aws_iam_role.aws_lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_scheduler_schedule" "daily_schedule" {
  name        = "bet-builder-gather-matches"
  description = "Run the bot each day at 00:00 to gather matches for current day."
  flexible_time_window {
    mode = "OFF"
  }
  target {
    arn      = aws_lambda_function.aws_lambda_function.arn
    role_arn = aws_iam_role.aws_lambda_role.arn
    input = jsonencode({
      "trigger_type" = "FIND_MATCHES"
    })
  }
  schedule_expression_timezone = "Europe/Bucharest"
  schedule_expression          = "cron(${var.daily_schedule_expression})"
  state                        = "DISABLED"
}

resource "aws_secretsmanager_secret" "aws_secrets" {
  for_each    = var.aws_secrets
  name        = each.key
  description = "Secret for ${each.key}"
}

resource "aws_secretsmanager_secret_version" "aws_secrets_version" {
  for_each      = var.aws_secrets
  secret_id     = aws_secretsmanager_secret.aws_secrets[each.key].id
  secret_string = jsonencode(each.value)
}