# bet-builder-bot

## Overview

**bet-builder-bot** is a personal attempt to test the viability of long-term low bets. It is an automated sports betting bot designed to interact with the Casa Pariurilor website. It uses Selenium to automate browser actions, schedules bets using AWS Lambda and EventBridge Scheduler, and manages secrets securely with AWS Secrets Manager. The bot is containerized for deployment as an AWS Lambda function using Docker.

## Features

- **Automated Login & Navigation:** Uses Selenium to log in and interact with the betting website.
- **Match Discovery & Scheduling:** Finds suitable matches and schedules bets using AWS EventBridge Scheduler.
- **Automated Bet Placement:** Places bets automatically at scheduled times.
- **Balance Checking:** Checks account balance before placing bets.
- **Email Notifications:** Sends info and error notifications via email (Gmail SMTP).
- **AWS Integration:** Uses Lambda, EventBridge Scheduler, ECR, IAM, and Secrets Manager.
- **Proxy Support:** All requests and browser actions are routed through a configurable proxy.

## Project Structure

- [`app/bot/`](app/bot/) - Core bot logic (login, scheduling, bet placement, selectors, base bot)
- [`app/utils/`](app/utils/) - Utilities (webdriver, headers, scheduler, secrets, email)
- [`app/config/`](app/config/) - Configuration files (YAML and loader)
- [`app/main.py`](app/main.py) - Lambda entrypoint
- [`Dockerfile`](Dockerfile) - Container definition for AWS Lambda
- [`main.tf`](main.tf), [`variables.tf`](variables.tf) - Terraform IaC for AWS resources

## Setup & Deployment

### Prerequisites

- Docker
- AWS CLI configured
- Terraform
- Python 3.9+ (for local testing)
- AWS account with permissions for Lambda, ECR, IAM, EventBridge, and Secrets Manager


### 1. Deploy AWS Infrastructure

```sh
terraform init
terraform plan
terraform apply
```

### 2. Build and Push Docker Image

```sh
./upload_image_to_ecr.sh
```

This will:
- Create ECR repo, Lambda function, IAM roles/policies, EventBridge schedule, and Secrets Manager secrets.

### 3. Configure Secrets

Update the `aws_secrets` variable in [`variables.tf`](variables.tf) or directly in AWS Secrets Manager with your credentials and proxy details.

### 4. Lambda Handler

The Lambda function entrypoint is [`main.lambda_handler`](app/main.py).

## Configuration

- Main config: [`app/config/config.yaml`](app/config/config.yaml)
- Secrets: Managed via AWS Secrets Manager (see `aws_secrets` in [`variables.tf`](variables.tf))

## How It Works

1. **Daily Schedule:** EventBridge triggers Lambda with `{"trigger_type": "FIND_MATCHES"}`.
2. **Match Discovery:** Bot finds matches and schedules individual bet events.
3. **Bet Placement:** At scheduled times, Lambda is triggered to place bets.
4. **Notifications:** Sends email notifications for info/errors.
5. **Error Handling:** Cleans up schedules and sends error emails on failure.

## Development

- All browser automation is handled via Selenium with Chrome in headless mode.
- Proxy settings are required for both HTTP requests and browser actions.
- Email notifications use Gmail SMTP (app password required).

## Security

- All sensitive data (credentials, proxy info) is stored in AWS Secrets Manager.
- IAM roles and policies are tightly scoped for Lambda and Scheduler.



---

**Note:** This bot is for educational purposes. Use responsibly and ensure compliance with the terms of service of any third-party services you interact with.