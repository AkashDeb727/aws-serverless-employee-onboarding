import boto3
import json

ses = boto3.client('ses')

def lambda_handler(event, context):

    employee_id = event.get("employeeId")
    email = event.get("email")
    current_stage = event.get("currentStage", "DOCUMENT_COLLECTION")

    response = ses.send_templated_email(
        Source="akashdeb727@gmail.com",
        Destination={
            'ToAddresses': [email]
        },
        Template='document_reminder_email',
        TemplateData=json.dumps({
            "firstName": "Employee",
            "currentStage": current_stage
        })
    )

    return {
        "statusCode": 200,
        "employeeId": employee_id,
        "messageId": response['MessageId']
    }