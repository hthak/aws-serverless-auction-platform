import json
import uuid
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("users")

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*"
    }

    try:
        body = json.loads(event.get("body") or "{}")

        name = body.get("name")
        acct_balance = body.get("acctBalance")

        if not name or acct_balance is None:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"message": "name and acctBalance are required"})
            }

        user_id = str(uuid.uuid4())

        item = {
            "userId": user_id,
            "name": name,
            "acctBalance": Decimal(str(acct_balance))
        }

        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "userId": user_id,
                "name": name,
                "acctBalance": float(acct_balance)
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"message": str(e)})
        }