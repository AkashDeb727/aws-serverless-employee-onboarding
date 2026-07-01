import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table(
    os.environ['TABLE_NAME']
)

def lambda_handler(event, context):

    employee_id = event['employeeId']
    stage = event['stage']
    status = event['status']

    timestamp = datetime.utcnow().isoformat()

    try:

        response = table.get_item(
            Key={
                'employeeId': employee_id
            }
        )

        item = response.get('Item')

        if item:

            history = item.get(
                'stageHistory',
                []
            )

            history.append({
                'stage': stage,
                'completedAt': timestamp
            })

            table.update_item(
                Key={
                    'employeeId': employee_id
                },
                UpdateExpression="""
                    SET currentStage=:stage,
                        workflowStatus=:status,
                        stageHistory=:history,
                        lastUpdated=:updated
                """,
                ExpressionAttributeValues={
                    ':stage': stage,
                    ':status': status,
                    ':history': history,
                    ':updated': timestamp
                }
            )

        else:

            table.put_item(
                Item={
                    'employeeId': employee_id,
                    'currentStage': stage,
                    'workflowStatus': status,
                    'stageHistory': [
                        {
                            'stage': stage,
                            'completedAt': timestamp
                        }
                    ],
                    'lastUpdated': timestamp
                }
            )

        return {
            'statusCode': 200,
            'body': json.dumps(
                'Progress Updated'
            )
        }

    except Exception as e:

        return {
            'statusCode': 500,
            'body': json.dumps(
                str(e)
            )
        }