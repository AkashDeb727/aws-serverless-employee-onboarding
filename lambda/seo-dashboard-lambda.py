import json
import os
import boto3
from decimal import Decimal
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb")

progress_table = dynamodb.Table(os.environ["PROGRESS_TABLE"])
employee_table = dynamodb.Table(os.environ["EMPLOYEE_TABLE"])

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,OPTIONS"
}


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def calculate_days(created_at):
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return (now - created).days
    except Exception:
        return 0


def lambda_handler(event, context):

    # Handle CORS preflight request
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": ""
        }

    try:

        progress_items = progress_table.scan().get("Items", [])

        dashboard = []

        for progress in progress_items:

            employee_id = progress["employeeId"]

            employee = employee_table.get_item(
                Key={
                    "employeeId": employee_id
                }
            ).get("Item", {})

            dashboard.append({
                "employeeId": employee_id,
                "name": employee.get("firstName", "") + " " + employee.get("lastName", ""),
                "department": employee.get("department", ""),
                "role": employee.get("role", ""),
                "currentStage": progress.get("currentStage"),
                "workflowStatus": progress.get("workflowStatus"),
                "daysInProcess": calculate_days(employee.get("createdAt", ""))
            })

        response = {
            "activeOnboardings": dashboard,
            "totalPending": len([
                x for x in dashboard
                if x["workflowStatus"] != "COMPLETED"
            ])
        }

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(response, cls=DecimalEncoder)
        }

    except Exception as e:

        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": str(e)
            })
        }