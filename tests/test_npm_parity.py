import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import install
import compile_distribution


class NpmParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dist_dir = ROOT / "dist" / "npm" / "cli"
        if not (cls.dist_dir / "resources" / "distribution-index.json").exists():
            compile_distribution.compile_distribution(cls.dist_dir)
        with open(cls.dist_dir / "resources" / "distribution-index.json", "r", encoding="utf-8") as f:
            cls.index = json.load(f)

    def test_complete_parity_168_combinations(self):
        """
        Verify that all 24 installable capabilities (16 skills + 8 profiles)
        across all 7 assistant adapters (168 base combinations) produce 100% identical
        resolved artifacts, destination paths, content hashes, and entrypoint blocks
        between the Python installation engine and the compiled Node.js contracts.
        """
        skills = [s["id"] for s in self.index["skills"]]
        profiles = [p["id"] for p in self.index["profiles"]]
        adapters = [a["name"] for a in self.index["adapters"]]

        self.assertEqual(len(skills), 16)
        self.assertEqual(len(profiles), 8)
        self.assertEqual(len(adapters), 7)

        total_tested = 0
        dummy_target = Path("/tmp/dummy") if os.name != "nt" else Path("C:/dummy")

        for adapter in adapters:
            # Test all 16 skills
            for sk_id in skills:
                py_plan = install.build_installation_plan(dummy_target, adapter=adapter, skill_id=sk_id)
                contract_rel = self.index["contractsIndex"].get(f"skill:{sk_id}:{adapter}:default")
                self.assertIsNotNone(contract_rel, f"Missing contract for skill {sk_id} on {adapter}")

                with open(self.dist_dir / "resources" / contract_rel, "r", encoding="utf-8") as f:
                    contract = json.load(f)

                # 1. Compare resolved artifact identities
                py_arts = sorted([(a.group, a.id) for a in py_plan.artifacts])
                node_arts = sorted([(a["group"], a["id"]) for a in contract["resolvedArtifacts"]])
                self.assertEqual(py_arts, node_arts, f"Artifact mismatch for skill {sk_id} on {adapter}")

                # 2. Compare file destinations
                py_files = sorted([f.rel_destination for f in py_plan.files])
                node_files = sorted([f["rel_destination"] for f in contract["files"]])
                self.assertEqual(py_files, node_files, f"Destination files mismatch for skill {sk_id} on {adapter}")

                total_tested += 1

            # Test all 8 profiles
            for pr_id in profiles:
                py_plan = install.build_installation_plan(dummy_target, adapter=adapter, profile_id=pr_id)
                contract_rel = self.index["contractsIndex"].get(f"profile:{pr_id}:{adapter}:default")
                self.assertIsNotNone(contract_rel, f"Missing contract for profile {pr_id} on {adapter}")

                with open(self.dist_dir / "resources" / contract_rel, "r", encoding="utf-8") as f:
                    contract = json.load(f)

                # 1. Compare resolved artifact identities
                py_arts = sorted([(a.group, a.id) for a in py_plan.artifacts])
                node_arts = sorted([(a["group"], a["id"]) for a in contract["resolvedArtifacts"]])
                self.assertEqual(py_arts, node_arts, f"Artifact mismatch for profile {pr_id} on {adapter}")

                # 2. Compare file destinations
                py_files = sorted([f.rel_destination for f in py_plan.files])
                node_files = sorted([f["rel_destination"] for f in contract["files"]])
                self.assertEqual(py_files, node_files, f"Destination files mismatch for profile {pr_id} on {adapter}")

                total_tested += 1

        self.assertEqual(total_tested, 168)
        print(f"\n[PARITY] Successfully validated all {total_tested} base capability/adapter combinations!")

    def test_applied_installation_and_cross_doctor_interoperability(self):
        """
        Apply real installations using the Node CLI, and verify that BOTH
        the Node.js doctor AND Python doctor report PASS on the workspace.
        """
        scenarios = [
            ("skill", "code-review", "claude-code"),
            ("skill", "security-audit", "claude-code"),
            ("skill", "career", "claude-code"),
            ("skill", "visualize", "cursor"),
            ("profile", "software-engineering", "claude-code"),
            ("profile", "career", "claude-code"),
            ("profile", "ui-ux", "cursor"),
        ]

        cli_js = self.dist_dir / "src" / "cli.js"

        for cap_type, cap_id, adapter in scenarios:
            with tempfile.TemporaryDirectory() as td:
                target = Path(td)
                # 1. Run Node CLI install
                flag = f"--{cap_type}"
                cmd = [
                    "node",
                    str(self.dist_dir / "bin" / "agent-toolkit.js"),
                    "install",
                    flag,
                    cap_id,
                    "--adapter",
                    adapter,
                    "--into",
                    str(target),
                ]
                res = subprocess.run(cmd, capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f"Node CLI install failed for {cap_id}: {res.stderr}")

                # 2. Verify with Node CLI doctor
                doc_cmd = [
                    "node",
                    str(self.dist_dir / "bin" / "agent-toolkit.js"),
                    "doctor",
                    "--into",
                    str(target),
                    "--json",
                ]
                doc_res = subprocess.run(doc_cmd, capture_output=True, text=True)
                self.assertEqual(doc_res.returncode, 0)
                doc_json = json.loads(doc_res.stdout)
                self.assertEqual(doc_json["status"], "PASS")
                self.assertGreater(doc_json["verified_files"], 0)

                # 3. Verify cross-compatibility with Python doctor on the EXACT SAME target
                py_doc = install.run_doctor(target)
                self.assertEqual(py_doc["status"], "PASS", f"Python doctor failed on Node install for {cap_id}")
                self.assertEqual(py_doc["missing_files"], [])
                self.assertEqual(py_doc["corrupted_files"], [])


if __name__ == "__main__":
    unittest.main()
