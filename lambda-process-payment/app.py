import json, os, base64

import boto3

kms = boto3.client("kms")
ddb = boto3.resource("dynamodb")
events = boto3.client("events")

KMS_ARN = os.environ["KMS_ARN"]
TABLE_NAME = os.environ["TABLE_NAME"]
TPP_CLIENT_ID = os.environ.get("TPP_CLIENT_ID")  # allowed TPP client

table = ddb.Table(TABLE_NAME)


def lambda_handler(event, context):
    try:
        # --- Authorization check: only TPP client with correct scope can call /payments ---
        auth_context = event.get("requestContext", {}).get("authorizer", {}).get("jwt", {})
        claims = auth_context.get("claims", {})

        client_id = claims.get("client_id") or claims.get("clientId")
        scope_str = claims.get("scope", "") or claims.get("scp", "")
        scopes = scope_str.split() if scope_str else []

        if client_id != TPP_CLIENT_ID or "payments-api/payments.tpp" not in scopes:
            return {
                "statusCode": 403,
                "body": "Forbidden: TPP-only payments endpoint."
            }

        # --- Business logic: detokenize and process payment ---
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

        # --- Emit PaymentEvent to EventBridge for fraud analysis ---
        try:
            events.put_events(
                Entries=[
                    {
                        "Source": "bank.payments",
                        "DetailType": "PaymentEvent",
                        "Detail": json.dumps({
                            "token": token,
                            "amount": amount
                        })
                    }
                ]
            )
        except Exception as e:
            # We do not fail the payment if event emission fails; we just log it.
            print(f"Failed to emit PaymentEvent: {e}")

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
