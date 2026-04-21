import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("bids")

def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(x) for x in obj]
    if isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    return obj

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*"
    }

    try:
        params = event.get("queryStringParameters") or {}
        auction_id = params.get("auctionId")

        if not auction_id:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"message": "auctionId is required"})
            }
        #code
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("auctionId").eq(auction_id),
            ScanIndexForward=False
        )

        items = decimal_to_native(response.get("Items", []))

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(items)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"message": str(e)})
        }