"""Compliance scanning file generators for Level 2 compliance documentation.

This module contains functions to generate compliance-specific scanning rules
and validation scripts for each supported framework (PCI-DSS, HIPAA, GDPR, etc.).
"""


def generate_level_2_compliance_scanning(
    compliance_packs: list[dict],
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

    return files
