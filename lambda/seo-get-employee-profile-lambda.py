import json
import boto3
import os
import base64

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

        auth = event["headers"].get("Authorization") or event["headers"].get("authorization")

        if not auth:
            raise Exception("Authorization header missing")

        token = auth.replace("Bearer ", "").strip()

        payload = token.split(".")[1]

        # Fix Base64 padding
        payload += "=" * (-len(payload) % 4)

        claims = json.loads(base64.urlsafe_b64decode(payload).decode())

        email = claims["email"]

        response = table.scan(
            FilterExpression="email = :e",
            ExpressionAttributeValues={
                ":e": email
            }
        )

        if not response["Items"]:
            return {
                "statusCode": 404,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": "Employee not found"
                })
            }

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(response["Items"][0])
        }

    except Exception as e:

        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": str(e)
            })
        }