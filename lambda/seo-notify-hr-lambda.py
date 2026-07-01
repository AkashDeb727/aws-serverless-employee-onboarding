import json

def lambda_handler(event, context):

    for record in event["Records"]:
        print("SNS Message:")
        print(record["Sns"]["Message"])

    return {
        "statusCode": 200,
        "body": json.dumps("HR notified successfully")
    }