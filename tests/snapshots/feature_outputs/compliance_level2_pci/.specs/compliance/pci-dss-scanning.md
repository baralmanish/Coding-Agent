---
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

<!-- user-custom:start:local -->
# Add project-specific guidance here.
<!-- user-custom:end:local -->
