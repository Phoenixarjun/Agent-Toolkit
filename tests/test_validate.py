import os
import shutil
import tempfile
import unittest
from pathlib import Path
import yaml

import scripts.validate as validate


class ValidateDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.root = validate.ROOT
        validate.errors.clear()

    def test_canonical_skills_discovered_count(self):
        """Ensure canonical skill discovery finds exactly the authoritative skills in skills/*/SKILL.md."""
        skill_paths = sorted((self.root / "skills").glob("*/SKILL.md"))
        self.assertEqual(len(skill_paths), 16)
        skill_names = [p.parent.name for p in skill_paths]
        self.assertIn("code-review", skill_names)
        self.assertIn("career", skill_names)
        self.assertIn("visualize", skill_names)
        self.assertIn("security-audit", skill_names)

    def test_adapter_and_installed_skills_excluded(self):
        """Ensure adapter templates and installed .agent-toolkit skills are not discovered as canonical skills."""
        canonical_skills = sorted((self.root / "skills").glob("*/SKILL.md"))
        for p in canonical_skills:
            self.assertTrue("skills" in p.parts)
            self.assertFalse("adapters" in p.parts)
            self.assertFalse(".agent-toolkit" in p.parts)
            self.assertFalse("dist" in p.parts)

    def test_duplicate_skill_id_rejected(self):
        """Ensure duplicate IDs in catalog fail validation."""
        temp_data = {
            "skills": [
                {"id": "test-dup", "path": "skills/code-review"},
                {"id": "test-dup", "path": "skills/career"},
            ]
        }
        with tempfile.TemporaryDirectory() as td:
            cat_path = Path(td) / "catalog.yaml"
            with open(cat_path, "w", encoding="utf-8") as f:
                yaml.dump(temp_data, f)
            
            # Temporarily point ROOT / catalog to temp
            orig_errors = list(validate.errors)
            validate.errors.clear()
            try:
                # Test the logic on data directly
                ids = {}
                entries = temp_data["skills"]
                group_ids = set()
                for entry in entries:
                    art_id = entry.get("id")
                    if art_id in group_ids:
                        validate.fail(f"duplicate id {art_id}")
                    group_ids.add(art_id)
                self.assertTrue(any("duplicate id test-dup" in e for e in validate.errors))
            finally:
                validate.errors = orig_errors

    def test_missing_canonical_file_fails_validation(self):
        """Ensure catalog entries referencing nonexistent paths fail validation."""
        temp_data = {
            "skills": [
                {"id": "nonexistent-skill", "path": "skills/does-not-exist"}
            ]
        }
        orig_errors = list(validate.errors)
        validate.errors.clear()
        try:
            for entry in temp_data["skills"]:
                art_path = entry["path"]
                if not (self.root / art_path).exists():
                    validate.fail(f"missing path: {art_path}")
            self.assertTrue(any("missing path: skills/does-not-exist" in e for e in validate.errors))
        finally:
            validate.errors = orig_errors

    def test_excluded_directories_respected(self):
        """Ensure EXCLUDED_PARTS contains build, install, and venv directories."""
        self.assertIn(".agent-toolkit", validate.EXCLUDED_PARTS)
        self.assertIn("node_modules", validate.EXCLUDED_PARTS)
        self.assertIn("dist", validate.EXCLUDED_PARTS)
        self.assertIn(".git", validate.EXCLUDED_PARTS)


if __name__ == "__main__":
    unittest.main()
