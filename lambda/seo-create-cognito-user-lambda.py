import json
import boto3
import os

cognito = boto3.client('cognito-idp')

USER_POOL_ID = os.environ['USER_POOL_ID']

def lambda_handler(event, context):

    email = event['email']
    employeeId = event['employeeId']

    response = cognito.admin_create_user(
        UserPoolId=USER_POOL_ID,
        Username=email,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email
            }
        ],
        TemporaryPassword='Temp@12345'
    )

    return {
        'statusCode': 200,
        'message': 'User created',
        'userName': response['User']['Username']
    }