import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


class ProductRealityIntegrationTests(unittest.TestCase):
    def test_skill_file_exists_and_valid(self):
        skill_path = ROOT / "skills" / "product-reality" / "SKILL.md"
        self.assertTrue(skill_path.exists(), f"Missing {skill_path}")
        text = skill_path.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"), "SKILL.md missing frontmatter")
        end = text.find("\n---\n", 4)
        self.assertNotEqual(end, -1, "SKILL.md unterminated frontmatter")
        frontmatter = yaml.safe_load(text[4:end])
        self.assertEqual(frontmatter.get("name"), "product-reality")
        self.assertTrue(frontmatter.get("description"), "Missing description")
        lines = len(text.splitlines())
        self.assertLessEqual(lines, 500, f"SKILL.md exceeds 500 lines ({lines})")

    def test_references_exist(self):
        ref_path = ROOT / "skills" / "product-reality" / "references" / "evidence-and-substitution.md"
        self.assertTrue(ref_path.exists(), f"Missing {ref_path}")

    def test_template_exists(self):
        template_path = ROOT / "templates" / "documents" / "PRODUCT-REALITY-REPORT.md"
        self.assertTrue(template_path.exists(), f"Missing {template_path}")

    def test_doc_exists_and_links_to_skill(self):
        doc_path = ROOT / "docs" / "skills" / "product-reality.md"
        self.assertTrue(doc_path.exists(), f"Missing {doc_path}")
        content = doc_path.read_text(encoding="utf-8")
        self.assertIn("../../skills/product-reality/SKILL.md", content)

    def test_evals_exist_and_valid(self):
        evals_path = ROOT / "evals" / "product-reality" / "cases.yaml"
        rubric_path = ROOT / "evals" / "product-reality" / "RUBRIC.md"
        self.assertTrue(evals_path.exists(), f"Missing {evals_path}")
        self.assertTrue(rubric_path.exists(), f"Missing {rubric_path}")
        data = yaml.safe_load(evals_path.read_text(encoding="utf-8"))
        self.assertEqual(data.get("skill"), "product-reality")
        cases = data.get("cases", [])
        self.assertGreaterEqual(len(cases), 30, f"Expected at least 30 cases, got {len(cases)}")
        for case in cases:
            self.assertIn("name", case)
            self.assertIn("input", case)
            self.assertIn("expect", case)
            self.assertIn("reject", case)

    def test_catalog_registration(self):
        catalog_path = ROOT / "catalog" / "catalog.yaml"
        data = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
        skill_ids = [s.get("id") for s in data.get("skills", [])]
        eval_ids = [e.get("id") for e in data.get("evals", [])]
        template_ids = [t.get("id") for t in data.get("templates", [])]

        self.assertIn("product-reality", skill_ids, "product-reality missing in catalog skills")
        self.assertIn("product-reality", eval_ids, "product-reality missing in catalog evals")
        self.assertIn("product-reality-report", template_ids, "product-reality-report missing in catalog templates")


if __name__ == "__main__":
    unittest.main()
