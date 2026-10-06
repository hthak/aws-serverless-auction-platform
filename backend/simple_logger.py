import json

def lambda_handler(event, context):
    print("Received event:")
    print(json.dumps(event))

    if "Records" in event:
        for record in event["Records"]:
            print("Record body:")
            print(record.get("body"))

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Event logged"})
    }