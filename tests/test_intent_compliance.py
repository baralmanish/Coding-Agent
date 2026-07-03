import unittest
from tests.helpers import load_bootstrap_module


mod = load_bootstrap_module()


class IntentComplianceTests(unittest.TestCase):
    def test_parse_compliance_input_aliases_and_dedup(self):
        keys = mod.parse_compliance_input("soc2,SOC-2,pci,gdpr,unknown")
        self.assertEqual(keys, ["soc2", "pci-dss", "gdpr"])

    def test_resolve_compliance_packs_auto_detects_from_intent(self):
        packs = mod.resolve_compliance_packs("wallet payments app", ["soc2"])
        keys = [pack["key"] for pack in packs]
        self.assertIn("soc2", keys)
        self.assertIn("pci-dss", keys)

    def test_resolve_app_blueprint_ranks_intents_with_framework_bonus(self):
        _, _, blueprint = mod.resolve_app_blueprint(
            "ride booking ecommerce payments",
            {"frameworks": ["Next.js"], "languages": ["TypeScript"]},
        )

        ranking = blueprint.get("intent_ranking", [])
        self.assertGreater(len(ranking), 0)
        self.assertEqual(ranking[0]["label"], "E-Commerce")
        self.assertGreaterEqual(ranking[0].get("framework_bonus", 0), 1)

    def test_known_intent_uses_starter_profile(self):
        key, raw, blueprint = mod.resolve_app_blueprint(
            "chatbot", {"frameworks": ["React"]}
        )
        self.assertEqual(key, "chatbot")
        self.assertEqual(raw, "chatbot")
        self.assertEqual(blueprint.get("label"), "Chatbot")

    def test_new_archetype_keywords_resolve_targeted_profile(self):
        _, _, blueprint = mod.resolve_app_blueprint(
            "insurance claims platform",
            {"frameworks": ["FastAPI"], "languages": ["Python"]},
        )

        labels = [item.get("label") for item in blueprint.get("intent_ranking", [])]
        self.assertIn("InsurTech", labels)
        self.assertIn("Policy lifecycle", " ".join(blueprint.get("capabilities", [])))

    def test_exact_archetype_keyword_input_boosts_ranking(self):
        _, _, blueprint = mod.resolve_app_blueprint(
            "proptech",
            {"frameworks": ["Next.js"], "languages": ["TypeScript"]},
        )

        ranking = blueprint.get("intent_ranking", [])
        self.assertGreater(len(ranking), 0)
        self.assertEqual(ranking[0]["label"], "PropTech")


if __name__ == "__main__":
    unittest.main()
