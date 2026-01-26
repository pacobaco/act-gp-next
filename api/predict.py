import json

def handler(request):
    # Example: return a static prediction
    prediction = {"prediction": "AI predicts success!"}
    return {
        "statusCode": 200,
        "body": json.dumps(prediction)
    }