import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):

    employeeId = event["employeeId"]
    taskToken = event["taskToken"]
    stage = event["stage"]

    table.put_item(
        Item={
            "employeeId": employeeId,
            "taskToken": taskToken,
            "stage": stage
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Task Token Stored Successfully"
        })
    }