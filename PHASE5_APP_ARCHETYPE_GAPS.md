# Phase 5 App Archetype Expansion

## Baseline

Keyword-driven intent profiles previously covered core domains such as analytics, ecommerce, ride booking, gov-tech, and ad-tech.

## New Business Patterns Added

1. InsurTech
2. PropTech
3. Manufacturing / MES
4. Nonprofit / Fundraising
5. Cybersecurity Platform
6. Climate / ESG

## Detection Logic Update

Intent resolution now applies a strong score boost when user input exactly matches:

- an archetype label slug, or
- one of an archetype's canonical keyword slugs.

This improves direct user inputs like "proptech" and "insurtech" so they rank correctly.

## Validation

- Added intent compliance tests for new patterns and exact-match boost behavior.
- Regenerated bootstrap and validated list-intents output includes all new patterns.
- Full test suite passes.
