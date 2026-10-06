import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb") #code
client = boto3.client("dynamodb")

auctions_table = dynamodb.Table("auctions")
bids_table = dynamodb.Table("bids")
users_table = dynamodb.Table("users")

def to_decimal(value):
    return Decimal(str(value))

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*"
    }

    try:
        body = json.loads(event.get("body") or "{}")
        auction_id = body.get("auctionId")

        if not auction_id:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"message": "auctionId is required"})
            }

        auction_resp = auctions_table.get_item(Key={"auctionId": auction_id})
        auction = auction_resp.get("Item")

        if not auction:
            return {
                "statusCode": 404,
                "headers": headers,
                "body": json.dumps({"message": "Auction not found"})
            }

        if auction.get("auctionStatus") != "open":
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"message": "Only open auctions can be closed"})
            }

        bids_resp = bids_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("auctionId").eq(auction_id),
            ScanIndexForward=False,
            Limit=1
        )
        bids = bids_resp.get("Items", [])

        if not bids:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"message": "Auction cannot be closed without bids"})
            }

        highest_bid = bids[0]
        winning_bid_amt = highest_bid["bidAmt"]
        winning_user_id = highest_bid["userId"]
        reserve = auction["reserve"]

        if winning_bid_amt < reserve:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"message": "Reserve has not been met"})
            }

        winner_resp = users_table.get_item(Key={"userId": winning_user_id})
        winner = winner_resp.get("Item")

        if not winner:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"message": "Winning user not found"})
            }

        current_balance = winner["acctBalance"]
        if current_balance < winning_bid_amt:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"message": "Winning user no longer has enough funds"})
            }

        new_balance = current_balance - winning_bid_amt

        client.transact_write_items(
            TransactItems=[
                {
                    "Update": {
                        "TableName": "auctions",
                        "Key": {
                            "auctionId": {"S": auction_id}
                        },
                        "UpdateExpression": "SET auctionStatus = :closed, winningUserId = :winner",
                        "ConditionExpression": "auctionStatus = :open",
                        "ExpressionAttributeValues": {
                            ":closed": {"S": "closed"},
                            ":winner": {"S": winning_user_id},
                            ":open": {"S": "open"}
                        }
                    }
                },
                {
                    "Update": {
                        "TableName": "users",
                        "Key": {
                            "userId": {"S": winning_user_id}
                        },
                        "UpdateExpression": "SET acctBalance = :newbal",
                        "ConditionExpression": "acctBalance >= :bidamt",
                        "ExpressionAttributeValues": {
                            ":newbal": {"N": str(new_balance)},
                            ":bidamt": {"N": str(winning_bid_amt)}
                        }
                    }
                }
            ]
        )

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "message": "Auction closed successfully",
                "auctionId": auction_id,
                "winningUserId": winning_user_id,
                "winningBid": float(winning_bid_amt)
            })
        }

    except client.exceptions.TransactionCanceledException:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"message": "Auction close failed transaction conditions"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"message": str(e)})
        }