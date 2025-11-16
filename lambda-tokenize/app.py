import json, os, uuid, base64
from datetime import datetime

import boto3

kms = boto3.client("kms")
ddb = boto3.resource("dynamodb")

KMS_ARN = os.environ["KMS_ARN"]
TABLE_NAME = os.environ["TABLE_NAME"]
table = ddb.Table(TABLE_NAME)


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        account = body.get("accountNumber")

        if not account:
            return {
                "statusCode": 400,
                "body": "Missing accountNumber"
            }

        # Encrypt the account number with KMS
        resp = kms.encrypt(
            KeyId=KMS_ARN,
            Plaintext=account.encode("utf-8")
        )
        ciphertext = base64.b64encode(resp["CiphertextBlob"]).decode("utf-8")

        token = str(uuid.uuid4())
        last4 = account[-4:]

        table.put_item(Item={
            "token": token,
            "ciphertext": ciphertext,
            "last4": last4,
            "created_at": datetime.utcnow().isoformat()
        })

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "token": token,
                "last4": last4
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
