import json

def handler(request):
    data = {"message": "This is a generate endpoint"}
    return {
        "statusCode": 200,
        "body": json.dumps(data)
    }