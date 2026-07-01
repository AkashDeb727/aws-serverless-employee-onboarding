import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,OPTIONS"
}


def lambda_handler(event, context):

    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": ""
        }

    try:
        employee_id = event["pathParameters"]["employeeId"]

        response = table.query(
            KeyConditionExpression=Key("employeeId").eq(employee_id)
        )

        documents = []

        for item in response.get("Items", []):
            documents.append({
                "documentType": item["documentType"],
                "status": item["status"]
            })

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "employeeId": employee_id,
                "documents": documents
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": str(e)
            })
        }