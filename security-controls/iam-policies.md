# IAM Policies for Banking APIs

IAM (Identity and Access Management) is the foundation of least-privilege enforcement in any regulated banking workload.  
In Open Banking and PCI DSS environments, IAM defines *who can do what* and ensures sensitive operations (like decrypting PANs or initiating payments) are tightly controlled and fully auditable.

This module documents the IAM patterns used across the AWS Banking Security Lab.

---

# 🎯 1. Objectives

By the end of this module, you will understand:

- IAM roles required by the `/accounts`, `/tokenize`, `/payments`, and fraud services  
- How IAM isolates sensitive operations like token vault decrypts  
- How Cognito + IAM together build a layered authorization model  
- IAM evidence needed for PCI DSS, Open Banking, and AWS FSI audits  

---

# 🧱 2. Core IAM Roles in This Architecture

| IAM Role | Purpose |
|----------|---------|
| **banking-lambda-execution-role** | Supports the `/accounts` API (Lab 01) |
| **banking-payments-role** | Grants tokenization + payments Lambdas access to KMS + DynamoDB (Lab 02) |
| **fraud-check-role** | Allows fraud detection Lambda to write alerts (Lab 04) |
| **tpp-client-role** (optional) | Represents automation or future machine identities |

Each role follows the Open Banking principle:

> **"Only the minimum privileges required for a single, well-defined purpose."**

---

# 🧩 3. Lambda Execution Role (Base Policy)

Every Lambda in AWS requires CloudWatch logging:

```json
{
  "Effect": "Allow",
  "Action": [
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ],
  "Resource": "*"
}
```

This satisfies:

AWS FSI Lens requirement → observability

PCI DSS Requirement 10 → audit logging

# 🔐 4. IAM for Tokenization (Payments Vault Access)

The Token Vault from Lab 02 is protected with KMS + DynamoDB.

Only the payments Lambdas may decrypt:

json
Copy code
{
  "Effect": "Allow",
  "Action": [
    "kms:Encrypt",
    "kms:Decrypt"
  ],
  "Resource": "arn:aws:kms:us-east-2:<account-id>:key/<token-vault-key-id>"
}
Why this matters:

Prevents other Lambdas from detokenizing

Enforces PCI DSS Key Access Controls (Req. 3)

Every decrypt is logged automatically by CloudTrail

# 📦 5. IAM for DynamoDB Token Vault Access

json
Copy code
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:PutItem",
    "dynamodb:GetItem",
    "dynamodb:UpdateItem"
  ],
  "Resource": "arn:aws:dynamodb:us-east-2:<account-id>:table/tokenization-vault"
}
This enforces:

Tokenization/de-tokenization can only happen within the payment microservices

Developers, admins, and other Lambdas cannot read or write vault entries

Helps restrict the Cardholder Data Environment (CDE)

# 🧪 6. IAM for Fraud Detection Services

The fraud engine in Lab 04 requires:

Read access to EventBridge event payload

Write access to the fraud-alerts DynamoDB table

Example:

json
Copy code
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:PutItem"
  ],
  "Resource": "arn:aws:dynamodb:us-east-2:<account-id>:table/fraud-alerts"
}
This ensures:

Fraud detection is isolated

Alerts cannot be overwritten or read by other services

Logs sent to CloudWatch are tamper-evident

# 🔑 7. IAM & Third-Party Providers (TPPs)

TPPs authenticate using:

OAuth2 Client Credentials, not IAM

IAM does not see TPP identities directly

However, IAM still governs:

Lambda permissions (backend services)

KMS encryption/decryption

DynamoDB writes

Logging + observability

Open Banking layering model:

Layer	Technology
Identity	Cognito (OAuth2/OIDC)
Authorization	OAuth scopes (payments.create)
Backend enforcement	IAM + Lambda + KMS policies

This creates a multi-layered trust boundary.

# 📑 8. Compliance & Audit Mapping

PCI DSS
Req 3: KMS encrypt/decrypt restrictions

Req 7: Least privilege IAM roles

Req 10: IAM role change logging (CloudTrail)

Open Banking / PSD2
Ensures strong segregation of internal functions

Prevents unauthorized access to payment data or PAN derivatives

AWS FSI Lens
“High criticality workload isolation”

“Strong identity controls”

IAM is at the center of all three frameworks.

# 📁 9. Evidence Generation (for Lab 05)

Recommended CloudTrail Lake queries:

Who decrypted sensitive data?
sql
Copy code
SELECT eventTime, userIdentity.principalId
FROM cloudtrail
WHERE eventSource='kms.amazonaws.com'
  AND eventName='Decrypt'
ORDER BY eventTime DESC;
Who changed IAM policies?
sql
Copy code
SELECT eventTime, eventName, userIdentity
FROM cloudtrail
WHERE eventSource='iam.amazonaws.com'
  AND eventName LIKE '%Policy%'
ORDER BY eventTime DESC;
Which Lambda roles accessed the vault?
sql
Copy code
SELECT userIdentity.principalId, eventName
FROM cloudtrail
WHERE requestParameters.keyId LIKE '%token-vault%'
ORDER BY eventTime DESC;
IAM is part of your compliance story.

# 🏁 10. Module Completed

You now have a complete, audit-ready IAM baseline for the Banking Security Lab.

Next module:

👉 “KMS Encryption & Key Policies”
