import json
import os
import boto3

ses = boto3.client("ses")

SENDER_EMAIL = os.environ["SENDER_EMAIL"]


def lambda_handler(event, context):

    employee_id = event["employeeId"]
    first_name = event["firstName"]
    last_name = event["lastName"]
    department = event["department"]
    role = event["role"]
    manager_email = event["managerEmail"]

    subject = "New Employee Ready for Introduction"

    body = f"""
Hello,

A new employee has completed the onboarding process and is ready for manager introduction.

Employee Details

Employee ID: {employee_id}
Name: {first_name} {last_name}
Department: {department}
Role: {role}

Please schedule an introduction meeting at your earliest convenience.

Regards,
HR Team
"""

    response = ses.send_email(
        Source=SENDER_EMAIL,
        Destination={
            "ToAddresses": [manager_email]
        },
        Message={
            "Subject": {
                "Data": subject
            },
            "Body": {
                "Text": {
                    "Data": body
                }
            }
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Manager introduction email sent successfully",
            "messageId": response["MessageId"]
        })
    }