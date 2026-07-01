import json
import boto3
import os
from datetime import datetime

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

bucket = os.environ["BUCKET_NAME"]
table = dynamodb.Table(os.environ["TABLE_NAME"])

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "POST,OPTIONS"
}


def lambda_handler(event, context):

    # Handle CORS preflight
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": ""
        }

    try:
        body = json.loads(event["body"])

        employeeId = body["employeeId"]
        documentType = body["documentType"]
        fileName = body["fileName"]

        key = f"{employeeId}/{documentType}_{fileName}"

        url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket,
                "Key": key
            },
            ExpiresIn=3600
        )

        table.put_item(
            Item={
                "employeeId": employeeId,
                "documentType": documentType,
                "status": "PENDING",
                "s3Key": key,
                "uploadDate": datetime.utcnow().isoformat()
            }
        )

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "uploadUrl": url,
                "expiresIn": 3600
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