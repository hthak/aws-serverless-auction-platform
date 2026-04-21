import json

def lambda_handler(event, context):
    print("Closed auction event received:")
    print(json.dumps(event))

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Event logged"})
    }