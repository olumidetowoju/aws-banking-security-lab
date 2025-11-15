# Compliance Mappings (PCI, FSI Lens, Open Banking)

Financial systems must not only *implement* security controls —  
they must *prove* that controls map to formal regulatory standards.

This module provides a unified mapping between the security patterns built in this AWS Banking Security Lab and the major compliance frameworks used in real financial institutions:

- **PCI DSS 4.0** (cardholder data protection)
- **Open Banking / PSD2 / FAPI** (secure financial APIs)
- **AWS Financial Services Industry (FSI) Lens** (regulated architectures)

---

# 🎯 1. Objectives

By the end of this module, you will understand:

- How each lab (01–05) maps to a regulatory requirement  
- How to describe your architecture in compliance language  
- Which AWS services support which compliance controls  
- How to produce “evidence packs” for auditors in Lab 05  

---

# 🧱 2. High-Level Compliance Overview

| Framework | Purpose |
|----------|----------|
| **PCI DSS 4.0** | Governs protection of PAN (Primary Account Number) & payments data |
| **Open Banking / PSD2** | Governs access by Third-Party Providers (TPPs), authentication, SCA |
| **FAPI (Financial-grade API)** | Profiles OAuth2/OIDC for financial APIs |
| **AWS FSI Lens** | AWS Well-Architected guidance for regulated workloads |

Each lab in the course contributes to one or more of these frameworks.

---

# 🔐 3. PCI DSS Mapping

This table maps key components from the labs to PCI DSS 4.0 requirements.

| Component | PCI Requirement | Explanation |
|----------|-----------------|-------------|
| **KMS Token Vault (Lab 02)** | **Req. 3.5 / 3.6** | Strong cryptography + strict key access control |
| **KMS Decrypt Logging (Lab 05)** | **Req. 10.2** | Logs access to CHD-related keys |
| **Cognito Auth (Labs 01–03)** | **Req. 8** | Strong authentication & user identity controls |
| **API Gateway + WAF** | **Req. 1.1 / 6.4** | Segmentation, secure API exposure |
| **CloudTrail Lake** | **Req. 10** | Centralized evidence + tamper-aware audit trail |
| **Fraud detection (Lab 04)** | **Req. 11** | Behavioral monitoring & anomaly detection |
| **Least privilege IAM roles** | **Req. 7** | Restrict access by business need-to-know |

**This lab series meets the architectural spirit of PCI DSS (not full implementation).**

---

# 🌍 4. Open Banking / PSD2 / FAPI Mapping

Open Banking focuses on **secure data sharing** and **strong customer authentication**.

| Requirement | Mapping to This Course |
|------------|-------------------------|
| **Strong Customer Authentication (SCA)** | Cognito OIDC + MFA (optional) |
| **TPP Identity** | OAuth2 Client Credentials (Lab 03) |
| **Fine-grained consent** | OAuth scopes (`payments.create`) |
| **Secure APIs** | API Gateway + TLS 1.2+ enforced |
| **Event-level auditability** | CloudTrail + API Gateway logs |
| **TPP vs Customer separation** | Different authorization models (Labs 01 vs 03) |
| **TPP certificate validation (FAPI/mTLS)** | Optional mTLS (Lab 03 advanced) |

These are the same principles used by Open Banking UK, PSD2, Australia CDR, Brazil Open Finance, etc.

---

# 🏦 5. AWS Financial Services Industry (FSI) Lens Mapping

AWS FSI Lens focuses on:

### ✔ Criticality-based isolation  
- Token vault in its own CMK domain  
- Lambda in private subnets  
- VPC endpoints for sensitive services  
- WAF-protected public API edges  

### ✔ Secure key management  
- CMK with strict key policies (Lab 02)  
- CloudTrail key usage logging (Lab 05)  

### ✔ Monitoring & observability  
- CloudTrail, Lake, CW Logs, API logs  
- Fraud alert logging (Lab 04)  

### ✔ Privileged access control  
- IAM least-privilege enforcement (Module 1 IAM)  

The Banking Labs reflect the **FSI Lens architecture blueprint**.

---

# 📑 6. End-to-End Laboratory Mapping

| Lab | Regulatory Concepts Demonstrated |
|-----|----------------------------------|
| **Lab 01: Accounts API** | Authentication, protected resource access, audit logging |
| **Lab 02: Tokenization** | Cryptographic protection of sensitive data, PCI DSS |
| **Lab 03: TPP Access** | PSD2 / Open Banking access control + scopes |
| **Lab 04: Fraud Detection** | Behavioral monitoring, anomaly detection |
| **Lab 05: Compliance Logging** | Evidence generation, SQL audit queries, non-repudiation |

Together, these labs form a simplified but **holistic Open Banking / PCI-aligned architecture.**

---

# 🧾 7. Evidence Pack Checklist (Lab 05)

This is the same type of “evidence pack” real banks present to regulators.

### 🔍 Identity & Access
- Cognito login logs (SCA)  
- IAM policy change history  

### 🔐 Cryptography
- CloudTrail logs for CMK `Decrypt` events  
- Key policy showing limited access  

### 🌐 Network
- API Gateway WAF logs  
- VPC Flow Logs (optional)  

### 💳 Payments & Tokenization
- Token vault DynamoDB entries  
- Encryption/decryption lifecycle evidence  

### 🧪 Fraud & Monitoring
- Fraud alerts DynamoDB table  
- EventBridge matched rules  
- Lambda fraud-check logs  

### 📊 Audit & Forensics
- CloudTrail Lake queries  
- Athena parquet/CSV exports  

This helps prove the platform is **secure, monitored, and compliant**.

---

# 🏁 8. Module Completed

You now have a complete compliance mapping framework for your AWS Banking Security Lab:

- PCI DSS  
- Open Banking / PSD2  
- FAPI  
- AWS FSI Lens  
