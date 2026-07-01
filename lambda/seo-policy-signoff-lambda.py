import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")
stepfunctions = boto3.client("stepfunctions")

progress_table = dynamodb.Table(os.environ["PROGRESS_TABLE"])
task_token_table = dynamodb.Table(os.environ["TASK_TOKEN_TABLE"])

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST"
}


def lambda_handler(event, context):

    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": ""
        }

    try:

        body = json.loads(event["body"])

        employeeId = body["employeeId"]
        agreedIT = body["agreedToITPolicy"]
        agreedHR = body["agreedToHRPolicy"]
        timestamp = body["signatureTimestamp"]

        if not agreedIT or not agreedHR:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": "All policies must be accepted."
                })
            }

        progress_table.update_item(
            Key={
                "employeeId": employeeId
            },
            UpdateExpression="SET policySignOff = :p",
            ExpressionAttributeValues={
                ":p": {
                    "agreedToITPolicy": agreedIT,
                    "agreedToHRPolicy": agreedHR,
                    "signatureTimestamp": timestamp
                }
            }
        )

        token = task_token_table.get_item(
            Key={
                "employeeId": employeeId
            }
        )

        if "Item" in token:

            item = token["Item"]

            if item.get("stage") == "POLICY_SIGNOFF":

                taskToken = item["taskToken"]

                stepfunctions.send_task_success(
                    taskToken=taskToken,
                    output=json.dumps({
                        "policySignOff": "SUCCESS",
                        "employeeId": employeeId
                    })
                )

                task_token_table.delete_item(
                    Key={
                        "employeeId": employeeId
                    }
                )

                print("Workflow resumed successfully.")

            else:

                print(
                    f"Task token belongs to stage '{item.get('stage')}', "
                    "not POLICY_SIGNOFF."
                )

        else:

            print("Task token not found.")

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": "Sign-off recorded successfully, proceeding to next stage."
            })
        }

    except Exception as e:

        print("Error:", str(e))

        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": str(e)
            })
        }