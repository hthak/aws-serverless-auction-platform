import json
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

        auction_id = body.get("auctionId")
        item_name = body.get("itemName")
        reserve = body.get("reserve")
        description = body.get("description")

        if not auction_id or not item_name or reserve is None or not description:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "auctionId, itemName, reserve, and description are required"
                })
            }

        item = {
            "auctionId": auction_id,
            "itemName": item_name,
            "reserve": Decimal(str(reserve)),
            "description": description,
            "auctionStatus": "open",
            "winningUserId": ""
        }

        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(auctionId)"
        )

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "auctionId": auction_id,
                "itemName": item_name,
                "reserve": float(reserve),
                "description": description,
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