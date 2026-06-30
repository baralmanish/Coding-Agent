"""Compliance scanning file generators for Level 2 compliance documentation.

This module contains functions to generate compliance-specific scanning rules
and validation scripts for each supported framework (PCI-DSS, HIPAA, GDPR, etc.).
"""


def _localization_tokens(locale: str) -> dict[str, str]:
    lang = (locale or "en").strip().lower()
    tokens = {
        "es": {
            "Scanning & Validation": "Escaneo y Validacion",
            "Code Scanning Rules": "Reglas de Escaneo de Codigo",
            "Configuration Validation": "Validacion de Configuracion",
            "Remediation Path": "Ruta de Remediacion",
            "Patterns & Implementation Examples": "Patrones y Ejemplos de Implementacion",
            "Implementation Patterns": "Patrones de Implementacion",
            "Acceptance Criteria": "Criterios de Aceptacion",
            "Validation Checks": "Verificaciones de Validacion",
            "Notes": "Notas",
        },
        "fr": {
            "Scanning & Validation": "Analyse et Validation",
            "Code Scanning Rules": "Regles d Analyse du Code",
            "Configuration Validation": "Validation de Configuration",
            "Remediation Path": "Parcours de Remediation",
            "Patterns & Implementation Examples": "Modeles et Exemples d Implementation",
            "Implementation Patterns": "Modeles d Implementation",
            "Acceptance Criteria": "Criteres d Acceptation",
            "Validation Checks": "Verifications de Validation",
            "Notes": "Notes",
        },
    }
    return tokens.get(lang, {})


def _apply_locale(content: str, locale: str) -> str:
    localized = content
    for source, target in _localization_tokens(locale).items():
        localized = localized.replace(source, target)
    return localized


def _apply_region_variant(content: str, compliance_region: str | None) -> str:
    region = (compliance_region or "").strip().lower()
    if not region:
        return content
    labels = {
        "eu": "EU regional guidance",
        "us": "US regional guidance",
        "apac": "APAC regional guidance",
        "latam": "LATAM regional guidance",
    }
    title = labels.get(region, f"{region.upper()} regional guidance")
    return (
        content.rstrip()
        + "\n\n"
        + f"## Regional Variant\n- Region: {region.upper()}\n- Profile: {title}\n"
    )


def _localize_and_apply_region(
    files: dict[str, str], locale: str, compliance_region: str | None
) -> dict[str, str]:
    adjusted = {}
    for path, content in files.items():
        localized = _apply_locale(content, locale)
        adjusted[path] = _apply_region_variant(localized, compliance_region)
    return adjusted


def generate_level_2_compliance_scanning(
    compliance_packs: list[dict],
    locale: str = "en",
    compliance_region: str | None = None,
) -> dict[str, str]:
    """Generate Level 2 compliance scanning rules and validation scripts."""
    files = {}

    # PCI-DSS scanning rules
    pci_packs = [p for p in compliance_packs if p.get("key") == "pci-dss"]
    if pci_packs:
        files[".specs/compliance/pci-dss-scanning.md"] = """---
title: PCI-DSS Scanning & Validation Rules
type: compliance-scanning
tags: [compliance, pci-dss, scanning, security]
related:
  - [[.specs/memory.md]]
---

# PCI-DSS: Scanning & Validation (Level 2)

Automated scanning rules and validation for payment security.

## Code Scanning Rules

### Rule: Plaintext Secrets in Code
- Search: regex patterns for hardcoded passwords, API keys, tokens
- Tools: `truffleHog`, `detect-secrets`, `gitleaks`
- Command: `gitleaks detect --source git --verbose`
- Fail: Any match found
- Exception: Test data marked with `@test-only` comments

### Rule: Encryption Algorithm Validation
- Search: `malloc`, `strcpy`, `md5`, `sha1` (weak hashing)
- Tools: `semgrep`, `sonarqube`
- Command: `semgrep --config=p/security-audit --json`
- Fail: Weak crypto detected in production code
- Exception: Legacy compatibility layer with deprecation notice

### Rule: SQL Injection Risk Patterns
- Search: Raw SQL concatenation without parameterization
- Tools: `sqlcheck`, `semgrep`
- Command: `semgrep --config=p/owasp-top-ten`
- Fail: Unparameterized queries in user-input handling paths
- Exception: Schema migrations (pre-approved)

## Configuration Validation

### Checklist
- [ ] TLS 1.2+ enforced for all cardholder data connections
- [ ] Certificate pinning implemented for API clients
- [ ] HSTS headers set (min-age: 31536000)
- [ ] CSP headers restrict inline scripts
- [ ] Session cookies marked Secure + HttpOnly + SameSite=Strict

### Validation Script
```bash
#!/bin/bash
# Check TLS version
openssl s_client -connect $HOST:443 -tls1_2 &>/dev/null || echo "FAIL: TLS 1.2 not supported"

# Check HSTS header
curl -I https://$HOST | grep -i "strict-transport-security" || echo "FAIL: HSTS missing"

# Check CSP header
curl -I https://$HOST | grep -i "content-security-policy" || echo "WARN: CSP missing"
```

## Dependency Audit Commands

### Pre-Commit
```bash
npm audit --audit-level=moderate
pip install safety && safety check
composer audit
```

### CI/CD Pipeline
```bash
# Node.js
npm ci && npm audit --production

# Python
pip install pip-audit && pip-audit

# Ruby
bundle audit check --update
```

### Incident Response
```bash
# Find vulnerable dependency usage
npm ls vulnerable-package
grep -r "vulnerable-package" src/

# Force audit on specific package
npm view vulnerable-package vulnerabilities
```

## Remediation Path
1. Scan code nightly and on every PR
2. Block merge if FAIL rules detected
3. Escalate HIGH/CRITICAL findings to security team
4. Document exceptions in compliance log
5. Re-scan after remediation
"""

    # HIPAA scanning rules (abbreviated for space)
    hipaa_packs = [p for p in compliance_packs if p.get("key") == "hipaa"]
    if hipaa_packs:
        files[".specs/compliance/hipaa-scanning.md"] = """---
title: HIPAA Scanning & Validation Rules
type: compliance-scanning
tags: [compliance, hipaa, scanning, security]
related:
  - [[.specs/memory.md]]
---

# HIPAA: Scanning & Validation (Level 2)

Automated scanning for PHI protection and audit logging.

## Code Scanning Rules

### Rule: PHI Data Exposure
- Search: PHI patterns (SSN, MRN, DOB) logged without redaction
- Tools: `semgrep`, custom regex scanner
- Command: `grep -r "\\\\d{{3}}-\\\\d{{2}}-\\\\d{{4}}" src/ --include="*.py" --include="*.js"`
- Fail: Unredacted PHI in logs or error messages
- Exception: Audit log with encrypted storage

## Remediation Path
1. Scan on every commit and nightly
2. Immediate escalation for PHI exposure
3. Incident response team notified
"""

    # GDPR, SOC2, CCPA, ISO27001 scanning rules (simplified)
    for framework_key, framework_name in [
        ("gdpr", "GDPR"),
        ("soc2", "SOC2"),
        ("ccpa", "CCPA/CPRA"),
        ("iso27001", "ISO 27001"),
    ]:
        packs = [p for p in compliance_packs if p.get("key") == framework_key]
        if packs:
            files[f".specs/compliance/{framework_key}-scanning.md"] = f"""---
title: {framework_name} Scanning & Validation Rules
type: compliance-scanning
tags: [compliance, {framework_key}, scanning, security]
related:
  - [[.specs/memory.md]]
---

# {framework_name}: Scanning & Validation (Level 2)

Automated scanning for {framework_name} compliance.

## Code Scanning Rules

Refer to compliance pack guidelines for specific rules and remediation paths.

## Configuration Validation

See compliance framework documentation for validation checklists.

## Remediation Path

1. Identify findings
2. Create tickets for remediation
3. Track resolution
4. Re-scan after fixes
5. Document in compliance log
"""

    return _localize_and_apply_region(files, locale, compliance_region)


def generate_level_3_compliance_patterns(
    compliance_packs: list[dict],
    locale: str = "en",
    compliance_region: str | None = None,
) -> dict[str, str]:
    """Generate Level 3 implementation pattern examples."""
    files = {}

    pci_packs = [p for p in compliance_packs if p.get("key") == "pci-dss"]
    if pci_packs:
        files[".specs/compliance/pci-dss-patterns.md"] = """---
title: PCI-DSS Implementation Patterns
type: compliance-patterns
tags: [compliance, pci-dss, patterns, implementation]
related:
  - [[.specs/memory.md]]
  - [[.specs/compliance/pci-dss-scanning.md]]
---

# PCI-DSS: Patterns & Implementation Examples (Level 3)

Production-ready examples for secure payment handling.

## Pattern 1: Tokenize Card Data at Ingress

### Python (FastAPI)
```python
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/payments/tokenize")
async def tokenize_card(payload: dict):
    pan = payload.get("pan", "")
    cvv = payload.get("cvv", "")
    if not pan or not cvv:
        raise HTTPException(status_code=400, detail="Missing card data")

    token = payment_gateway.tokenize(pan=pan, cvv=cvv)
    # Never persist raw PAN or CVV.
    return {"card_token": token, "last4": pan[-4:]}
```

### Node.js (Express)
```javascript
app.post('/payments/tokenize', async (req, res) => {
  const { pan, cvv } = req.body;
  if (!pan || !cvv) return res.status(400).json({ error: 'Missing card data' });

  const token = await paymentGateway.tokenize({ pan, cvv });
  return res.json({ cardToken: token, last4: pan.slice(-4) });
});
```

### Go (net/http)
```go
func TokenizeCard(w http.ResponseWriter, r *http.Request) {
    var req struct { PAN string `json:"pan"`; CVV string `json:"cvv"` }
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "invalid payload", http.StatusBadRequest)
        return
    }
    if req.PAN == "" || req.CVV == "" {
        http.Error(w, "missing card data", http.StatusBadRequest)
        return
    }

    token := paymentGateway.Tokenize(req.PAN, req.CVV)
    _ = json.NewEncoder(w).Encode(map[string]string{"cardToken": token, "last4": req.PAN[len(req.PAN)-4:]})
}
```

## Pattern 2: Encryption at Rest for Payment Metadata

### Python
```python
def store_payment_metadata(order_id: str, card_token: str, customer_id: str):
    encrypted = kms_encrypt_json(
        {
            "card_token": card_token,
            "customer_id": customer_id,
        },
        key_alias="alias/payments",
    )
    db.execute(
        "INSERT INTO payment_metadata(order_id, encrypted_blob) VALUES (%s, %s)",
        [order_id, encrypted],
    )
```

## Pattern 3: Structured Audit Trail (No Sensitive Values)

```json
{
  "event": "payment_authorized",
  "actor": "service:checkout-api",
  "order_id": "ord_12345",
  "card_last4": "4242",
  "result": "approved",
  "trace_id": "trace-abc-123"
}
```

## Acceptance Criteria
1. PAN and CVV are not persisted or logged.
2. Only gateway-issued tokens are stored in application systems.
3. Payment metadata is encrypted at rest with managed keys.
4. Audit logs are immutable and redact sensitive fields.

## Validation Checks
- Run `gitleaks detect --source .` on each pull request.
- Block deploy if static analysis finds weak cryptography or SQL injection paths.
- Verify production logs contain no PAN/CVV patterns.

## Notes
- Keep gateway credentials in a secrets manager.
- Rotate encryption keys and validate decryption in disaster recovery drills.
"""

    hipaa_packs = [p for p in compliance_packs if p.get("key") == "hipaa"]
    if hipaa_packs:
        files[".specs/compliance/hipaa-patterns.md"] = """---
title: HIPAA Implementation Patterns
type: compliance-patterns
tags: [compliance, hipaa, patterns, implementation]
related:
    - [[.specs/memory.md]]
    - [[.specs/compliance/hipaa-scanning.md]]
---

# HIPAA: Patterns & Implementation Examples (Level 3)

Reference patterns for protecting PHI and preserving auditability.

## Pattern 1: PHI Redaction in Logs

```python
import re

SSN_RE = re.compile(r"\\b\\d{3}-\\d{2}-\\d{4}\\b")

def redact_phi(value: str) -> str:
        return SSN_RE.sub("***-**-****", value)

def safe_log(message: str) -> None:
        logger.info(redact_phi(message))
```

## Pattern 2: Access Checks Before PHI Read

```python
def fetch_patient_record(patient_id: str, actor: User):
        if not rbac.can(actor, "patient.read", patient_id):
                raise PermissionError("Access denied")
        return patient_repo.get(patient_id)
```

## Pattern 3: Immutable Audit Event

```json
{
    "event": "phi_record_accessed",
    "actor": "user:clinician-42",
    "patient_id": "pt_9012",
    "purpose": "treatment",
    "trace_id": "trace-hipaa-001"
}
```

## Acceptance Criteria
1. PHI fields are redacted from application logs.
2. PHI reads require explicit authorization checks.
3. Access events are logged with actor, purpose, and trace metadata.
"""

    gdpr_packs = [p for p in compliance_packs if p.get("key") == "gdpr"]
    if gdpr_packs:
        files[".specs/compliance/gdpr-patterns.md"] = """---
title: GDPR Implementation Patterns
type: compliance-patterns
tags: [compliance, gdpr, patterns, implementation]
related:
    - [[.specs/memory.md]]
    - [[.specs/compliance/gdpr-scanning.md]]
---

# GDPR: Patterns & Implementation Examples (Level 3)

Reference patterns for consent, minimization, and deletion workflows.

## Pattern 1: Consent Gate for Optional Processing

```typescript
function canRunMarketingProfile(user: User): boolean {
    return user.consent?.marketing === true;
}
```

## Pattern 2: Data Minimization in API Response

```typescript
function toPublicUser(u: UserRecord) {
    return {
        id: u.id,
        displayName: u.displayName,
    };
}
```

## Pattern 3: Right-to-Erasure Job

```python
def erase_user_data(user_id: str):
        user_repo.delete_profile(user_id)
        event_repo.delete_by_user(user_id)
        object_storage.delete_prefix(f"users/{user_id}/")
```

## Acceptance Criteria
1. Optional processing requires explicit consent flags.
2. APIs return only data required for the current purpose.
3. Deletion workflows remove data from primary and derived stores.
"""

    soc2_packs = [p for p in compliance_packs if p.get("key") == "soc2"]
    if soc2_packs:
        files[".specs/compliance/soc2-patterns.md"] = """---
title: SOC2 Implementation Patterns
type: compliance-patterns
tags: [compliance, soc2, patterns, implementation]
related:
    - [[.specs/memory.md]]
    - [[.specs/compliance/soc2-scanning.md]]
---

# SOC2: Patterns & Implementation Examples (Level 3)

Reference patterns for access control, change logging, and service reliability.

## Pattern 1: Role-Based Action Guard

```python
def require_role(user: User, role: str) -> None:
        if role not in user.roles:
                raise PermissionError(f"Missing role: {role}")
```

## Pattern 2: Change Audit Event

```json
{
    "event": "config_changed",
    "actor": "user:ops-admin-7",
    "resource": "billing.service.timeout",
    "old": "20s",
    "new": "30s",
    "ticket": "CHG-2419"
}
```

## Pattern 3: Health Check Contract

```typescript
app.get('/healthz', (_req, res) => {
    res.status(200).json({ status: 'ok', version: process.env.RELEASE_SHA });
});
```

## Acceptance Criteria
1. Privileged actions enforce explicit role checks.
2. Security-relevant configuration changes are audit logged.
3. Service health endpoints provide deterministic readiness signals.
"""

    ccpa_packs = [p for p in compliance_packs if p.get("key") == "ccpa"]
    if ccpa_packs:
        files[".specs/compliance/ccpa-patterns.md"] = """---
title: CCPA/CPRA Implementation Patterns
type: compliance-patterns
tags: [compliance, ccpa, cpra, patterns, implementation]
related:
    - [[.specs/memory.md]]
    - [[.specs/compliance/ccpa-scanning.md]]
---

# CCPA/CPRA: Patterns & Implementation Examples (Level 3)

Reference patterns for consumer rights handling and sale/share controls.

## Pattern 1: Do-Not-Sell Enforcement

```typescript
function canShareForAds(profile: ConsumerProfile): boolean {
    return profile.optOutSaleShare !== true;
}
```

## Pattern 2: Consumer Request Export

```python
def export_consumer_data(consumer_id: str) -> dict:
        return {
                "profile": profile_repo.get(consumer_id),
                "events": event_repo.list_by_consumer(consumer_id),
                "preferences": pref_repo.get(consumer_id),
        }
```

## Pattern 3: Consumer Deletion Ticket

```json
{
    "event": "consumer_deletion_requested",
    "consumer_id": "c_1827",
    "request_id": "dsr-9921",
    "status": "queued"
}
```

## Acceptance Criteria
1. Ad-tech sharing is disabled when consumer opts out.
2. Access/export responses include all required consumer data categories.
3. Deletion requests are tracked from intake through completion.
"""

    iso_packs = [p for p in compliance_packs if p.get("key") == "iso27001"]
    if iso_packs:
        files[".specs/compliance/iso27001-patterns.md"] = """---
title: ISO27001 Implementation Patterns
type: compliance-patterns
tags: [compliance, iso27001, patterns, implementation]
related:
    - [[.specs/memory.md]]
    - [[.specs/compliance/iso27001-scanning.md]]
---

# ISO 27001: Patterns & Implementation Examples (Level 3)

Reference patterns for control ownership, risk treatment, and incident readiness.

## Pattern 1: Control Ownership Registry

```yaml
controls:
    A.8.2:
        owner: security-platform
        evidence: s3://evidence/asset-classification/
    A.12.4:
        owner: sre
        evidence: s3://evidence/logging-monitoring/
```

## Pattern 2: Risk Register Entry

```json
{
    "risk_id": "R-117",
    "asset": "customer-data-api",
    "likelihood": "medium",
    "impact": "high",
    "treatment": "enable WAF + stricter rate limits",
    "owner": "platform-security"
}
```

## Pattern 3: Incident Runbook Trigger

```bash
#!/usr/bin/env bash
set -euo pipefail
incidentctl create --severity high --service customer-data-api --summary "Potential data exposure"
```

## Acceptance Criteria
1. Controls have defined owners and retrievable evidence links.
2. Risks include treatment plans and accountable owners.
3. Security incidents can be raised with a standardized, repeatable workflow.
"""

    return _localize_and_apply_region(files, locale, compliance_region)
