import json
import boto3

from datetime import datetime


def create_schedule(schedule_name: str, start_date: datetime, payload: dict) -> dict:
    """Function to create a schedule for the Lambda function."""
    schedule_client = boto3.client("scheduler")
    lambda_client = boto3.client("lambda")

    lambda_function_name = "bet-builder-lambda-function"
    lambda_details = lambda_client.get_function(FunctionName=lambda_function_name)

    cron_expression = f"cron({start_date.minute} {start_date.hour} {start_date.day} {start_date.month} ? {start_date.year})"

    response = schedule_client.create_schedule(
        Name=schedule_name,
        ScheduleExpressionTimezone="Europe/Bucharest",
        ScheduleExpression=cron_expression,
        FlexibleTimeWindow={"Mode": "OFF"},
        Target={
            "Arn": lambda_details["Configuration"]["FunctionArn"],
            "RoleArn": lambda_details["Configuration"]["Role"],
            "Input": json.dumps(payload),
        },
    )
    return response


def delete_schedule(schedule_name: str) -> dict:
    """Function to delete a schedule for the Lambda function."""
    try:
        schedule_client = boto3.client("scheduler")
        schedule_client.delete_schedule(Name=schedule_name)
        print(f"Schedule {schedule_name} deleted.")
    except Exception:
        pass


def delete_all_schedules():
    """
    Function to delete all available schedules in EventBridge.
    Should only be used if we reached a point of no coming back
    and human intervention is required.
    """
    schedule_client = boto3.client("scheduler")
    for schedule in schedule_client.list_schedules()["Schedules"]:
        try:
            schedule_client.delete_schedule(Name=schedule["Name"])
            print(f"Schedule {schedule['Name']} deleted.")
        except Exception:
            continue
