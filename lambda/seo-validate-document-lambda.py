import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")
stepfunctions = boto3.client("stepfunctions")

document_table = dynamodb.Table(os.environ["TABLE_NAME"])
task_token_table = dynamodb.Table(os.environ["TASK_TOKEN_TABLE"])
topic_arn = os.environ["SNS_TOPIC_ARN"]


def lambda_handler(event, context):

    try:

        record = event["Records"][0]
        key = record["s3"]["object"]["key"]

        print("S3 KEY:", key)

        if key.endswith("/"):
            return {
                "statusCode": 200,
                "body": json.dumps("Folder ignored")
            }

        parts = key.split("/")

        if len(parts) < 2:
            raise Exception("Invalid S3 Key")

        employeeId = parts[0]
        filename = parts[1]

        if filename.startswith("GOVERNMENT_ID"):
            documentType = "GOVERNMENT_ID"
        elif filename.startswith("TAX_FORM"):
            documentType = "TAX_FORM"
        elif filename.startswith("PASSPORT"):
            documentType = "PASSPORT"
        elif filename.startswith("RESUME"):
            documentType = "RESUME"
        else:
            raise Exception(f"Unknown document type: {filename}")

        print("Employee ID:", employeeId)
        print("Document Type:", documentType)

        # Update document status
        document_table.update_item(
            Key={
                "employeeId": employeeId,
                "documentType": documentType
            },
            UpdateExpression="SET #status = :s",
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":s": "VERIFIED"
            }
        )

        # Notify HR
        sns.publish(
            TopicArn=topic_arn,
            Subject="Document Verified",
            Message=f"{employeeId}'s {documentType} has been verified."
        )

        # Retrieve stored task token
        token_response = task_token_table.get_item(
            Key={
                "employeeId": employeeId
            }
        )

        if "Item" in token_response:

            item = token_response["Item"]

            if item.get("stage") == "DOCUMENT_COLLECTION":

                task_token = item["taskToken"]

                stepfunctions.send_task_success(
                    taskToken=task_token,
                    output=json.dumps({
                        "documentVerificationStatus": "SUCCESS",
                        "employeeId": employeeId
                    })
                )

                # Delete token after successful callback
                task_token_table.delete_item(
                    Key={
                        "employeeId": employeeId
                    }
                )

                print("Workflow resumed successfully.")

            else:

                print(
                    f"Task token belongs to stage '{item.get('stage')}', "
                    "not DOCUMENT_COLLECTION."
                )

        else:

            print("No task token found for employee.")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Document Verified Successfully"
            })
        }

    except Exception as e:

        print("Error:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }