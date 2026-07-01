import json
import boto3
import os

ses = boto3.client("ses")

SENDER = "2403A51028@sru.edu.in"
TEMPLATE_NAME = "welcome_employee_email"

def lambda_handler(event, context):

    print("Received Event:", event)

    receiver = event["email"]

    first_name = event.get("firstName", "Employee")
    employee_id = event.get("employeeId", "N/A")
    username = event.get("email")
    temporary_password = event.get("temporaryPassword", "Temp@12345")

    response = ses.send_templated_email(
        Source=SENDER,
        Destination={
            "ToAddresses": [receiver]
        },
        Template=TEMPLATE_NAME,
        TemplateData=json.dumps({
            "firstName": first_name,
            "employeeId": employee_id,
            "username": username,
            "temporaryPassword": temporary_password
        })
    )

    print("SES Response:", response)

    return {
        "statusCode": 200,
        "message": "Templated email sent successfully"
    }