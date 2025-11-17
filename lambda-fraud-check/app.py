import json, os, uuid
from datetime import datetime

import boto3

ddb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]
table = ddb.Table(TABLE_NAME)


def lambda_handler(event, context):
    """
    EventBridge sends a single event with:
      - source = "bank.payments"
      - detail-type = "PaymentEvent"
      - detail = { "token": "...", "amount": 123 }

    We apply simple rules:
      - amount > 5000 -> suspicious
      - amount < 0 -> suspicious

    Suspicious events are written to the fraud-alerts table.
    """
    # Extract token and amount from the EventBridge detail
    detail = event.get("detail", {})
    token = detail.get("token")
    amount = detail.get("amount")

    if token is None or amount is None:
        # nothing to do
        return {
            "statusCode": 200,
            "body": json.dumps({"alerts_created": 0})
        }

    reasons = []

    if amount > 5000:
        reasons.append("HIGH_AMOUNT")

    if amount < 0:
        reasons.append("NEGATIVE_AMOUNT")

    if not reasons:
        # not suspicious
        return {
            "statusCode": 200,
            "body": json.dumps({"alerts_created": 0})
        }

    alert_id = str(uuid.uuid4())

    item = {
        "alertId": alert_id,
        "token": token,
        "amount": amount,
        "reasons": ",".join(reasons),
        "timestamp": datetime.utcnow().isoformat()
    }

    table.put_item(Item=item)

    return {
        "statusCode": 200,
        "body": json.dumps({"alerts_created": 1})
    }
