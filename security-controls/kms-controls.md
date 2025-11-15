# KMS Encryption & Key Policies

AWS Key Management Service (KMS) is the cryptographic anchor of every secure financial system.  
In regulated industries (PCI DSS, Open Banking, FSI), encryption alone is not enough — you must prove **who** accessed **what**, **when**, and **why**.

This module defines the KMS strategy used across the AWS Banking Security Lab and explains how key policies, IAM policies, and CloudTrail create a complete audit chain.

---

# 🎯 1. Objectives

After this module, you will understand:

- How to design CMKs (Customer Managed Keys) for banking workloads  
- Why tokenization requires its own dedicated CMK  
- How key policies enforce least privilege at the cryptographic layer  
- How CloudTrail logs KMS operations for compliance  
- PCI DSS & Open Banking mapping for KMS controls  

---

# 🔐 2. The Token Vault CMK

For the tokenization system (Lab 02), you created a **dedicated CMK**:

**Key Name:**  
banking-token-vault-key

powershell
Copy code

**Purpose:**  
Encrypt and decrypt sensitive “payment account numbers” (simulation of PANs).

**Why a dedicated CMK?**

- Separates cryptographic domains  
- Reduces PCI DSS scope  
- Supports key rotation independently  
- Prevents cross-service “data leakage”  
- Clear audit trail: “Who decrypted payment data?”  

---

# 🧱 3. Example Key Policy (Banking-Grade)

This is a simplified but correct KMS key policy for the token vault:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::<account-id>:root" },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<account-id>:role/banking-payments-role"
      },
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt"
      ],
      "Resource": "*"
    }
  ]
}
```

Breakdown
Root principal retains full administrative control

banking-payments-role (Lab 02 Lambda role) may Encrypt/Decrypt

No other roles, services, or users can decrypt vault data

CloudTrail logs every decrypt

This enforces strict cryptographic segmentation.

# 🔒 4. Lambda KMS Usage Policy

The IAM role for tokenization (payments role) should explicitly allow:

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
Best practices:

✔ Encrypt only inside the tokenization Lambda
✔ Decrypt only inside the detokenization Lambda
✔ Never decrypt data in:
API Gateway

TPP clients

Customer-facing Lambdas

Developer environments

This ensures raw data never leaves the secure vault boundary.

# 🔍 5. Key Separation Strategy

In real banks, one CMK → one domain:

Domain	CMK
Token Vault	banking-token-vault-key
Fraud Engine Secrets	Separate CMK
Customer PII	Separate CMK
Logging/Export Control	Separate CMK

This aligns with:

PCI DSS 3.1: Restrict access to cardholder data by business need-to-know

FSI Lens: “Data classification & isolation”

Open Banking: Segregation of payment data vs identity data

# 🧪 6. How CloudTrail Monitors KMS

Every cryptographic operation is tracked:

kms:Encrypt

kms:Decrypt

kms:GenerateDataKey

kms:ScheduleKeyDeletion

kms:DisableKey

This enables cryptographic non-repudiation, a key requirement for regulated workloads.

Example CloudTrail Lake Query (Lab 05):

sql
Copy code
SELECT eventTime, userIdentity.principalId, requestParameters
FROM   cloudtrail
WHERE  eventSource = 'kms.amazonaws.com'
  AND  eventName = 'Decrypt'
ORDER BY eventTime DESC;
This answers:

“Which Lambda decrypted sensitive payment data last night?”

# 📘 7. Compliance Mapping

🔐 PCI DSS 4.0
Req. 3.5 – Protect cryptographic keys from unauthorized access

Req. 3.6 – Document & enforce key management processes

Req. 10.2 – Log all access to keys and CHD

Req. 7 – Limit key access to personnel/roles with need-to-know

🌍 Open Banking / PSD2 / FAPI
Strong cryptography for payment data

Non-repudiation via logged key operations

Segregated access rights

🏦 AWS FSI Lens
“High criticality workloads must use customer-managed encryption keys”

“Keys must have clear administrators and users”

# 🧾 8. Evidence Generation (Used in Lab 05)

Suggested CloudTrail Lake filters:

Who decrypted the token vault?
sql
Copy code
SELECT eventTime, userIdentity.principalId
FROM cloudtrail
WHERE eventSource='kms.amazonaws.com'
  AND eventName='Decrypt';
Who modified the CMK?
sql
Copy code
SELECT eventTime, eventName, userIdentity
FROM cloudtrail
WHERE eventSource='kms.amazonaws.com'
  AND eventName LIKE '%Key%';
Were any unauthorized decrypt attempts made?
sql
Copy code
SELECT *
FROM cloudtrail
WHERE errorCode IS NOT NULL
  AND eventSource='kms.amazonaws.com';

# 🏁 9. Module Completed

You now have a complete, audit-ready KMS strategy for the Banking Security Lab:

Dedicated CMK for token vault

Restricted decryption to payments-only Lambdas

CloudTrail monitoring for all key usage

Compliance mapping to PCI DSS, FSI Lens, and Open Banking

Next module:

👉 “Module 3 – Network Controls (VPC, SG, NACL, WAF)”
