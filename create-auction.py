import json
import uuid
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("auctions")

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*"
    }

    try:
        body = json.loads(event.get("body") or "{}")

        item_name = body.get("itemName")
        description = body.get("description")
        reserve = body.get("reserve")

        if not item_name or not description or reserve is None:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"message": "itemName, description, and reserve are required"})
            }

        auction_id = str(uuid.uuid4())

        item = {
            "auctionId": auction_id,
            "itemName": item_name,
            "description": description,
            "reserve": Decimal(str(reserve)),
            "auctionStatus": "open",
            "winningUserId": ""
        }

        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "auctionId": auction_id,
                "itemName": item_name,
                "description": description,
                "reserve": float(reserve),
                "auctionStatus": "open",
                "winningUserId": ""
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"message": str(e)})
        }