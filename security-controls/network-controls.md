# Network Controls (VPC, Security Groups, NACL, WAF)

Network security is a foundational requirement for any financial-grade architecture.  
In regulated environments (PCI DSS, Open Banking, FSI), network controls provide **segmentation**, **traffic filtering**, and **defense-in-depth** for APIs, microservices, and sensitive data paths.

This module defines network design and enforcement strategies used throughout the AWS Banking Security Lab.

---

# 🎯 1. Objectives

By the end of this module, you will understand:

- Why VPC boundaries matter in banking workloads  
- How to isolate sensitive Lambda functions and data stores  
- How API Gateway, WAF, SGs, and NACLs complement each other  
- How PCI DSS maps to AWS network controls  
- How to design segmentation for Open Banking and payments flows  

---

# 🧱 2. VPC Architecture for Banking APIs

Even though Lambda can run without a VPC, **regulated architectures** use VPCs to isolate sensitive workloads:

### Recommended layout:

| Network Area | Purpose |
|--------------|---------|
| **Private subnets** | Payment processing, token vault Lambdas |
| **Public subnets** | NAT gateways, API Gateway custom domains |
| **VPC Endpoints** | DynamoDB, KMS, S3, CloudWatch Logs |
| **Restricted outbound access** | Prevent accidental external calls |

### Common VPC Endpoints used in these labs:

com.amazonaws.us-east-2.dynamodb
com.amazonaws.us-east-2.kms
com.amazonaws.us-east-2.logs
com.amazonaws.us-east-2.s3

### Why?
- Prevents data from ever leaving AWS backbone  
- PCI DSS requires segmentation inside the CDE (Cardholder Data Environment)  
- Reduces attack surface significantly  

---

# 🔐 3. Security Groups (SGs) — Micro-Segmentation Layer

Security Groups enforce **instance-level** (Lambda, EC2, RDS) ingress/egress rules.

Recommended SG configuration for Lambda microservices:

### Lambda SG (payments, tokenization, fraud processing)

| Rule Type | Rule |
|-----------|------|
| **Inbound** | None (Lambda does not receive inbound) |
| **Outbound** | Only HTTPS to VPC endpoints |

Example outbound-only SG rule:

Outbound:
HTTPS (443) → com.amazonaws.us-east-2.dynamodb
HTTPS (443) → com.amazonaws.us-east-2.kms
HTTPS (443) → com.amazonaws.us-east-2.logs

**Avoid:**  
`0.0.0.0/0` outbound — even though AWS often allows it, banks do not.

### Why SGs matter

- They enforce network-level least privilege  
- They prevent Lambda from calling arbitrary endpoints  
- They satisfy PCI DSS network segmentation requirements  
- They add a second layer beneath IAM  

---

# 🚧 4. Network ACLs (NACLs) — Subnet-Level Guardrails

NACLs work at the **subnet** level, not at the instance level.

Best practices for this lab:

- Leave NACLs in **default ALLOW ALL** mode unless needed  
- Introduce DENY rules only for:
  - Blocking known bad IPs
  - Geo-blocking
  - External restricted ranges

NACLs are **stateless**, unlike SGs, so they require symmetric inbound/outbound rules.

### When to use NACLs in banking:

- Large-scale blocking  
- Zero-trust subnet segmentation  
- Compliance-driven guardrails  

But for Lambda-centric designs, **SGs are usually enough**.

---

# 🛡️ 5. AWS WAF for API Gateway

AWS WAF protects all internet-facing banking APIs from:

- Injection attacks  
- XSS  
- Bot traffic  
- Enumeration attacks  
- Credential stuffing  
- High-volume bursts (rate limiting)  

Attach WAF → API Gateway Stage (for all labs).

### Recommended Managed Rules:

- AWSManagedRulesCommonRuleSet  
- AWSManagedRulesSQLiRuleSet  
- AWSManagedRulesKnownBadInputsRuleSet  
- Bot Control (optional)  
- Anonymous IP List (optional)  
- Geo Restriction (optional)

### Example baseline ACL logic:

Allow → Verified traffic
Block → SQL injection attempts
Block → XSS attempts
Block → Bot attacks
Block → High-frequency anomalous calls

This matches Open Banking standards for public API exposure.

---

# 🌐 6. API Gateway Edges + Network Controls

API Gateway combinations:

| Component | Role |
|----------|-------|
| **TLS 1.2+ enforced** | Required for financial APIs |
| **WAF → Stage** | Protects API entry point |
| **JWT Authorizer** | Authenticates customer/TPP |
| **Rate limiting** | Controls burst/flood attacks |
| **VPC links** (future) | Private microservices access |

API Gateway is the **boundary** between the public internet and the bank’s internal processing environment.

---

# 🧪 7. Monitoring & Telemetry

Network controls generate logs for detection and investigation:

| Source | Log Type |
|--------|----------|
| WAF | Blocked requests, attack signatures |
| API Gateway | Access logs (identity, latency, errors) |
| VPC Flow Logs | Subnet/SG traffic visibility |
| CloudTrail | API-level network configuration changes |

These logs feed directly into **Lab 05**:

- Evidence pack generation  
- Investigating fraud attempts  
- Analyzing TPP behavior  
- Tracing PCI-relevant events  

---

# 📘 8. Compliance & Regulatory Mapping

### PCI DSS 4.0
- **Req 1.1:** Network segmentation  
- **Req 1.4:** Protection of CDE from untrusted networks  
- **Req 10:** Logging of access to network resources  

### Open Banking (PSD2 / FAPI)
- Strong perimeter controls around public APIs  
- API security enforced at the edge  
- Denial-of-service protection  

### AWS Financial Services Industry Lens
- High-criticality workload isolation  
- Controlled egress  
- Network boundary protection  

---

# 🏁 9. Module Completed

You now understand how VPC, SGs, NACLs, and WAF form a **defense-in-depth network perimeter** for your Open Banking platform.

Next up:

👉 **Module 4 — Compliance Mappings (PCI, FSI, Open Banking)**  
