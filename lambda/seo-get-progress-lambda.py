import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")

TABLE_NAME = "employee_onboarding_progress_tracking"
table = dynamodb.Table(TABLE_NAME)

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


def lambda_handler(event, context):

    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": ""
        }

    try:
        employee_id = event["pathParameters"]["employeeId"]

        response = table.get_item(
            Key={
                "employeeId": employee_id
            }
        )

        if "Item" not in response:
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": "Employee not found"
                })
            }

        item = response["Item"]

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "employeeId": item.get("employeeId"),
                "currentStage": item.get("currentStage"),
                "workflowStatus": item.get("workflowStatus"),
                "lastUpdated": item.get("lastUpdated"),
                "stageHistory": item.get("stageHistory", [])
            }, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": str(e)
            })
        }