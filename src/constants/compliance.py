"""Compliance framework definitions and mappings."""

COMPLIANCE_PACKS = {
    "pci-dss": {
        "name": "PCI DSS",
        "trigger_keywords": [
            "wallet",
            "ewallet",
            "payments",
            "fintech",
            "checkout",
            "commerce",
        ],
        "checks": [
            "Tokenize payment data and avoid storing PAN/CVV in application systems.",
            "Enforce network segmentation and least-privilege access for payment paths.",
            "Run regular vulnerability scans and monitored audit trails for card workflows.",
        ],
    },
    "hipaa": {
        "name": "HIPAA",
        "trigger_keywords": [
            "health",
            "clinic",
            "ehr",
            "emr",
            "telemedicine",
            "patient",
        ],
        "checks": [
            "Restrict PHI access with role-based controls and just-in-time authorization.",
            "Encrypt PHI in transit and at rest with key rotation and access logs.",
            "Maintain breach response procedures and immutable access audit trails.",
        ],
    },
    "soc2": {
        "name": "SOC 2",
        "trigger_keywords": ["saas", "b2b", "enterprise", "tenant"],
        "checks": [
            "Document change management and approval workflows for production releases.",
            "Enforce periodic access reviews, offboarding, and least-privilege controls.",
            "Track availability/security incidents and corrective actions with evidence.",
        ],
    },
    "gdpr": {
        "name": "GDPR",
        "trigger_keywords": [
            "social",
            "analytics",
            "adtech",
            "tracking",
            "marketing",
            "profile",
        ],
        "checks": [
            "Implement consent management and lawful-basis tracking for personal data.",
            "Support data subject rights: export, correction, deletion, and processing restrictions.",
            "Apply data minimization and retention policies with enforcement automation.",
        ],
    },
    "ccpa": {
        "name": "CCPA/CPRA",
        "trigger_keywords": ["social", "analytics", "adtech", "consumer", "tracking"],
        "checks": [
            "Implement do-not-sell/share controls and consumer data access requests.",
            "Classify personal information categories and purpose of use.",
            "Audit third-party data sharing and contractual obligations.",
        ],
    },
    "iso27001": {
        "name": "ISO 27001",
        "trigger_keywords": [
            "enterprise",
            "gov",
            "government",
            "public-sector",
            "b2b",
            "saas",
        ],
        "checks": [
            "Maintain risk register, treatment plans, and control ownership evidence.",
            "Define asset inventory and classification with handling requirements.",
            "Run incident response exercises and control effectiveness reviews.",
        ],
    },
}

COMPLIANCE_ALIASES = {
    "pci": "pci-dss",
    "pcidss": "pci-dss",
    "pci-dss": "pci-dss",
    "hipaa": "hipaa",
    "soc2": "soc2",
    "soc-2": "soc2",
    "gdpr": "gdpr",
    "ccpa": "ccpa",
    "cpra": "ccpa",
    "iso27001": "iso27001",
    "iso-27001": "iso27001",
}
