variable "aws_region" {
  description = "The AWS region to deploy the resources in"
  type        = string
  default     = "eu-north-1"
}

variable "aws_ecr_repository_name" {
  description = "The name of the ECR repository"
  type        = string
  default     = "bet-builder"
}

variable "aws_lambda_function_name" {
  description = "The name of the Lambda function"
  type        = string
  default     = "bet-builder-lambda-function"
}

variable "aws_account_id" {
  description = "The AWS account ID"
  type        = string
  default     = "905418056526"
}

variable "daily_schedule_expression" {
  description = "The schedule expression for the daily schedule"
  type        = string
  default     = "0 23 * * ? *"
}

variable "aws_secrets" {
  description = "The AWS secrets for the Lambda function"
  type        = map(any)
  default = {
    "bet-builder-secrets" = {
      "bet_app_username" : "",
      "bet_app_password" : "",
      "gmail_app_password" = "",
      "from_address"       = "",
      "to_address"         = "",
      "proxy_user" : "",
      "proxy_password" : "",
      "proxy_host" : "",
      "proxy_port" : 33335
    }
  }
}