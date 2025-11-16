import json, os, base64

import boto3

kms = boto3.client("kms")
ddb = boto3.resource("dynamodb")

KMS_ARN = os.environ["KMS_ARN"]
TABLE_NAME = os.environ["TABLE_NAME"]
table = ddb.Table(TABLE_NAME)


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        token = body.get("token")
        amount = body.get("amount")

        if not token or amount is None:
            return {
                "statusCode": 400,
                "body": "token and amount are required"
            }

        resp = table.get_item(Key={"token": token})
        item = resp.get("Item")
        if not item:
            return {
                "statusCode": 404,
                "body": "Invalid token"
            }

        ciphertext = base64.b64decode(item["ciphertext"])

        # Decrypt the stored ciphertext with KMS
        dec = kms.decrypt(
            CiphertextBlob=ciphertext,
            KeyId=KMS_ARN
        )
        account_number = dec["Plaintext"].decode("utf-8")

        result = {
            "token": token,
            "account": f"****{item['last4']}",
            "amount": amount,
            "status": "APPROVED"
        }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
