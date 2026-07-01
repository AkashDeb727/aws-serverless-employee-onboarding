import json
import boto3
import uuid
import os
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb")
lambda_client = boto3.client("lambda")
stepfunctions = boto3.client("stepfunctions")

TABLE_NAME = os.environ["TABLE_NAME"]
COGNITO_LAMBDA = os.environ["COGNITO_LAMBDA"]
EMAIL_LAMBDA = os.environ["EMAIL_LAMBDA"]
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]

table = dynamodb.Table(TABLE_NAME)

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "OPTIONS,POST"
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

        employee_id = str(uuid.uuid4())

        first_name = body["firstName"]
        last_name = body["lastName"]
        email = body["email"]
        department = body["department"]
        role = body["role"]
        manager_email = body["managerEmail"]

        created_at = datetime.now(timezone.utc).isoformat()

        print(f"Registering employee: {email}")

        table.put_item(
            Item={
                "employeeId": employee_id,
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "department": department,
                "role": role,
                "managerEmail": manager_email,
                "createdAt": created_at
            }
        )

        print("Employee saved to DynamoDB")

        cognito_response = lambda_client.invoke(
            FunctionName=COGNITO_LAMBDA,
            InvocationType="RequestResponse",
            Payload=json.dumps({
                "employeeId": employee_id,
                "email": email
            }).encode("utf-8")
        )

        print("Cognito Status Code:", cognito_response["StatusCode"])
        print("Cognito Function Error:", cognito_response.get("FunctionError"))
        print(cognito_response["Payload"].read().decode())

        email_response = lambda_client.invoke(
            FunctionName=EMAIL_LAMBDA,
            InvocationType="RequestResponse",
            Payload=json.dumps({
                "employeeId": employee_id,
                "firstName": first_name,
                "email": email,
                "temporaryPassword": "Temp@12345"
            }).encode("utf-8")
        )

        print("Email Status Code:", email_response["StatusCode"])
        print("Email Function Error:", email_response.get("FunctionError"))
        print(email_response["Payload"].read().decode())

        workflow_response = stepfunctions.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps({
                "employeeId": employee_id,
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "department": department,
                "role": role,
                "managerEmail": manager_email
            })
        )

        print("Workflow Started")
        print(workflow_response)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": "Employee Registered Successfully",
                "employeeId": employee_id
            })
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Registration Failed",
                "message": str(e)
            })
        }