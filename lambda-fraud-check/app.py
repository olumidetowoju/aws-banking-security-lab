import json, os, uuid
from datetime import datetime

import boto3

ddb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]
table = ddb.Table(TABLE_NAME)


def lambda_handler(event, context):
    """
    EventBridge will send a batch of PaymentEvent records.
    We apply simple rules:
      - amount > 5000 -> suspicious
      - negative amount -> suspicious
    Suspicious events are written to fraud-alerts table.
    """
    alerts_created = 0

    for record in event.get("Records", []):
        detail = record.get("detail", {})
        token = detail.get("token")
        amount = detail.get("amount")

        if token is None or amount is None:
            continue

        reasons = []

        if amount > 5000:
            reasons.append("HIGH_AMOUNT")

        if amount < 0:
            reasons.append("NEGATIVE_AMOUNT")

        if not reasons:
            continue

        alert_id = str(uuid.uuid4())

        item = {
            "alertId": alert_id,
            "token": token,
            "amount": amount,
            "reasons": ",".join(reasons),
            "timestamp": datetime.utcnow().isoformat()
        }

        table.put_item(Item=item)
        alerts_created += 1

    return {
        "statusCode": 200,
        "body": json.dumps({"alerts_created": alerts_created})
    }
