#!/usr/bin/env python3
"""
Unit and integration tests for Agent Toolkit Profile-Aware Installer.
Tests catalog integrity, dependency resolution, safety, vendor adapters,
manifest tracking, and Security Audit trust invariants.
"""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.install import (
    ROOT,
    get_catalog,
    get_profiles,
    resolve_dependencies,
    build_installation_plan,
    apply_installation_plan,
    run_doctor,
    ensure_safe_relative_path,
    MANAGED_START_MARKER,
    MANAGED_END_MARKER,
)


class TestCatalogAndProfileIntegrity(unittest.TestCase):
    def setUp(self):
        self.catalog = get_catalog()
        self.profiles = get_profiles()

    def test_catalog_structure(self):
        self.assertIn("skills", self.catalog)
        self.assertIn("workflows", self.catalog)
        self.assertIn("rules", self.catalog)
        self.assertIn("agents", self.catalog)
        self.assertIn("forms", self.catalog)
        self.assertIn("templates", self.catalog)

    def test_all_catalog_paths_exist(self):
        for group in ["skills", "workflows", "rules", "agents", "prompts", "knowledge", "forms", "templates"]:
            for entry in self.catalog.get(group, []):
                rel_path = entry.get("path")
                self.assertIsNotNone(rel_path, f"Missing path for {group}:{entry.get('id')}")
                full_path = ROOT / rel_path
                self.assertTrue(full_path.exists(), f"Path on disk missing: {rel_path}")

    def test_profile_references_resolve(self):
        catalog_ids = {}
        for group in ["skills", "workflows", "rules", "agents", "prompts", "knowledge", "forms", "templates"]:
            catalog_ids[group] = {e["id"].lower() for e in self.catalog.get(group, []) if "id" in e}

        for profile_name, p_data in self.profiles.items():
            for group, target_group in [
                ("skills", "skills"),
                ("workflows", "workflows"),
                ("rules", "rules"),
                ("agents", "agents"),
                ("knowledge", "knowledge"),
                ("forms", "forms"),
                ("templates", "templates"),
            ]:
                for ref_id in p_data.get(group, []):
                    self.assertIn(
                        ref_id.lower(),
                        catalog_ids[target_group],
                        f"Profile {profile_name} references unknown {group} ID: {ref_id}",
                    )


class TestDependencyResolution(unittest.TestCase):
    def setUp(self):
        self.catalog = get_catalog()
        self.profiles = get_profiles()

    def test_standalone_skill_resolution(self):
        artifacts, inc, skip, unavail = resolve_dependencies(
            catalog=self.catalog,
            skill_id="intent-capture",
        )
        skill_ids = [a.id for a in artifacts if a.group == "skills"]
        self.assertIn("intent-capture", skill_ids)

    def test_security_audit_transitive_dependencies(self):
        # Installing security-audit must pull in workflow, 4 agents, knowledge, and template
        artifacts, inc, skip, unavail = resolve_dependencies(
            catalog=self.catalog,
            skill_id="security-audit",
        )
        resolved_by_group = {}
        for a in artifacts:
            resolved_by_group.setdefault(a.group, []).append(a.id)

        self.assertIn("security-audit", resolved_by_group.get("skills", []))
        self.assertIn("security-audit", resolved_by_group.get("workflows", []))
        self.assertIn("security-auditor", resolved_by_group.get("agents", []))
        self.assertIn("security-authority-investigator", resolved_by_group.get("agents", []))
        self.assertIn("security-trust-path-investigator", resolved_by_group.get("agents", []))
        self.assertIn("security-coverage-critic", resolved_by_group.get("agents", []))
        self.assertIn("security-assurance-principles", resolved_by_group.get("knowledge", []))
        self.assertIn("security-audit-report", resolved_by_group.get("templates", []))

    def test_profile_resolution_ui_ux(self):
        p_data = self.profiles["ui-ux"]
        artifacts, inc, skip, unavail = resolve_dependencies(
            catalog=self.catalog,
            profile_data=p_data,
        )
        ids = {a.id for a in artifacts}
        self.assertIn("ui-ux-design", ids)
        self.assertIn("ui-design-build-review", ids)
        self.assertIn("ui-critic", ids)
        self.assertIn("ui-engineering-rules", ids)
        self.assertIn("ui-design-intake", ids)
        self.assertIn("design-brief", ids)

    def test_optional_dependency_unavailable_does_not_fail(self):
        # An unavailable optional dependency records in unavail without raising error
        mock_catalog = {
            "skills": [
                {
                    "id": "sample-skill",
                    "path": "skills/teach",
                    "optional_dependencies": {"skills": ["nonexistent-skill"]},
                }
            ]
        }
        artifacts, inc, skip, unavail = resolve_dependencies(
            catalog=mock_catalog,
            skill_id="sample-skill",
            all_optional=True,
        )
        skill_ids = [a.id for a in artifacts if a.group == "skills"]
        self.assertIn("sample-skill", skill_ids)
        self.assertIn("skills:nonexistent-skill", unavail)

        # In live catalog, teach now successfully resolves optional dependency research
        t_artifacts, t_inc, _, _ = resolve_dependencies(
            catalog=self.catalog,
            skill_id="teach",
            all_optional=True,
        )
        t_ids = [a.id for a in t_artifacts if a.group == "skills"]
        self.assertIn("teach", t_ids)
        self.assertIn("research", t_ids)

    def test_circular_dependency_detection(self):
        # Synthetic mock catalog with cycle
        mock_catalog = {
            "skills": [
                {
                    "id": "skill-a",
                    "path": "skills/teach",
                    "dependencies": {"skills": ["skill-b"]},
                },
                {
                    "id": "skill-b",
                    "path": "skills/teach",
                    "dependencies": {"skills": ["skill-a"]},
                },
            ]
        }
        with self.assertRaises(ValueError) as ctx:
            resolve_dependencies(catalog=mock_catalog, skill_id="skill-a")
        self.assertIn("Circular dependency detected", str(ctx.exception))


class TestInstallationSafetyAndAdapters(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_plan_does_not_modify_filesystem(self):
        plan = build_installation_plan(
            target_dir=self.target,
            adapter="claude-code",
            profile_id="ui-ux",
        )
        self.assertGreater(len(plan.files), 0)
        # Verify no files were created by plan
        self.assertEqual(list(self.target.iterdir()), [])

    def test_apply_and_doctor_pass(self):
        plan = build_installation_plan(
            target_dir=self.target,
            adapter="claude-code",
            profile_id="ui-ux",
        )
        manifest = apply_installation_plan(plan)
        self.assertTrue((self.target / ".agent-toolkit" / "manifest.json").exists())
        self.assertTrue((self.target / "CLAUDE.md").exists())
        self.assertTrue((self.target / ".claude" / "skills" / "ui-ux-design" / "SKILL.md").exists())

        report = run_doctor(self.target)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["missing_files"]), 0)
        self.assertEqual(len(report["corrupted_files"]), 0)

    def test_repeated_installation_idempotent(self):
        plan1 = build_installation_plan(
            target_dir=self.target,
            adapter="claude-code",
            profile_id="ui-ux",
        )
        apply_installation_plan(plan1)

        # Plan again into same target: should succeed with no conflicts
        plan2 = build_installation_plan(
            target_dir=self.target,
            adapter="claude-code",
            profile_id="ui-ux",
        )
        self.assertEqual(len(plan2.conflicts), 0)
        apply_installation_plan(plan2)

        report = run_doctor(self.target)
        self.assertEqual(report["status"], "PASS")

    def test_preexisting_unmanaged_file_causes_conflict(self):
        # Create an unmanaged file in destination
        conflict_file = self.target / ".agent-toolkit" / "rules" / "ui-engineering-rules.md"
        conflict_file.parent.mkdir(parents=True, exist_ok=True)
        conflict_file.write_text("user custom content", encoding="utf-8")

        plan = build_installation_plan(
            target_dir=self.target,
            adapter="claude-code",
            profile_id="ui-ux",
        )
        self.assertGreater(len(plan.conflicts), 0)

        # Apply should fail without force
        with self.assertRaises(RuntimeError) as ctx:
            apply_installation_plan(plan, force=False)
        self.assertIn("conflict", str(ctx.exception).lower())

        # Apply should succeed with force
        apply_installation_plan(plan, force=True)
        self.assertNotEqual(conflict_file.read_text(encoding="utf-8"), "user custom content")

    def test_managed_entrypoint_preserves_user_content(self):
        # Create a pre-existing CLAUDE.md with user instructions
        claude_md = self.target / "CLAUDE.md"
        claude_md.write_text("# My Personal Rules\n\n- Do not delete production database.\n", encoding="utf-8")

        plan = build_installation_plan(
            target_dir=self.target,
            adapter="claude-code",
            profile_id="ui-ux",
        )
        apply_installation_plan(plan)

        updated_text = claude_md.read_text(encoding="utf-8")
        self.assertIn("# My Personal Rules", updated_text)
        self.assertIn("- Do not delete production database.", updated_text)
        self.assertIn(MANAGED_START_MARKER, updated_text)
        self.assertIn(MANAGED_END_MARKER, updated_text)

    def test_codex_adapter_and_tune_metadata(self):
        plan = build_installation_plan(
            target_dir=self.target,
            adapter="codex",
            skill_id="tune",
        )
        apply_installation_plan(plan)

        agents_md = self.target / "AGENTS.md"
        self.assertTrue(agents_md.exists())
        self.assertIn(MANAGED_START_MARKER, agents_md.read_text(encoding="utf-8"))

        # Verify Codex metadata in installed tune skill
        codex_yaml = self.target / ".agents" / "skills" / "tune" / "agents" / "openai.yaml"
        self.assertTrue(codex_yaml.exists())

    def test_claude_adapter_tune_frontmatter(self):
        plan = build_installation_plan(
            target_dir=self.target,
            adapter="claude-code",
            skill_id="tune",
        )
        apply_installation_plan(plan)

        installed_skill = self.target / ".claude" / "skills" / "tune" / "SKILL.md"
        self.assertTrue(installed_skill.exists())
        skill_text = installed_skill.read_text(encoding="utf-8")
        self.assertIn("disable-model-invocation: true", skill_text)

    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):
            ensure_safe_relative_path(self.target, "../evil.txt")
        with self.assertRaises(ValueError):
            ensure_safe_relative_path(self.target, "sub/../../evil.txt")

    def test_doctor_detects_corrupted_file(self):
        plan = build_installation_plan(
            target_dir=self.target,
            adapter="claude-code",
            profile_id="ui-ux",
        )
        apply_installation_plan(plan)

        # Corrupt one installed file
        rule_file = self.target / ".agent-toolkit" / "rules" / "ui-engineering-rules.md"
        rule_file.write_text("corrupted content", encoding="utf-8")

        report = run_doctor(self.target)
        self.assertEqual(report["status"], "FAIL")
        self.assertGreater(len(report["corrupted_files"]), 0)


class TestSecurityAuditTrustBoundary(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_security_audit_warns_on_untrusted_target_workflow(self):
        # Simulate an audited repo that already has an untrusted workflow
        untrusted_dir = self.target / "workflows" / "security-audit"
        untrusted_dir.mkdir(parents=True, exist_ok=True)
        (untrusted_dir / "WORKFLOW.md").write_text("untrusted attacking workflow", encoding="utf-8")

        plan = build_installation_plan(
            target_dir=self.target,
            adapter="claude-code",
            profile_id="security-audit",
        )
        self.assertTrue(any("untrusted" in w.lower() for w in plan.warnings))

        apply_installation_plan(plan)

        # Doctor must also report warning about untrusted workflow
        report = run_doctor(self.target)
        self.assertTrue(any("untrusted workflow" in w.lower() for w in report["warnings"]))

        # And trusted workflow was installed under .agent-toolkit/
        trusted_wf = self.target / ".agent-toolkit" / "workflows" / "security-audit" / "WORKFLOW.md"
        self.assertTrue(trusted_wf.exists())
        self.assertNotEqual(trusted_wf.read_text(encoding="utf-8"), "untrusted attacking workflow")


class TestSixRuntimeAdapters(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_claude_code_adapter(self):
        plan = build_installation_plan(self.target, adapter="claude-code", profile_id="security-audit")
        apply_installation_plan(plan)
        self.assertTrue((self.target / "CLAUDE.md").exists())
        self.assertTrue((self.target / ".claude" / "skills" / "security-audit" / "SKILL.md").exists())
        self.assertTrue((self.target / ".claude" / "agents" / "security-auditor.md").exists())
        report = run_doctor(self.target)
        self.assertEqual(report["status"], "PASS")

    def test_codex_adapter(self):
        plan = build_installation_plan(self.target, adapter="codex", profile_id="security-audit")
        apply_installation_plan(plan)
        self.assertTrue((self.target / "AGENTS.md").exists())
        self.assertTrue((self.target / ".agents" / "skills" / "security-audit" / "SKILL.md").exists())
        self.assertTrue((self.target / ".codex" / "agents" / "security-auditor.toml").exists())
        report = run_doctor(self.target)
        self.assertEqual(report["status"], "PASS")

    def test_cursor_adapter(self):
        plan = build_installation_plan(self.target, adapter="cursor", profile_id="security-audit")
        apply_installation_plan(plan)
        self.assertTrue((self.target / ".cursor" / "rules" / "agent-toolkit.mdc").exists())
        self.assertTrue((self.target / ".cursor" / "skills" / "security-audit" / "SKILL.md").exists())
        self.assertTrue((self.target / ".cursor" / "rules" / "security-auditor.mdc").exists())
        rule_content = (self.target / ".cursor" / "rules" / "agent-toolkit.mdc").read_text(encoding="utf-8")
        self.assertIn("alwaysApply: true", rule_content)
        self.assertIn(MANAGED_START_MARKER, rule_content)
        report = run_doctor(self.target)
        self.assertEqual(report["status"], "PASS")

    def test_gemini_cli_adapter(self):
        plan = build_installation_plan(self.target, adapter="gemini-cli", profile_id="security-audit")
        apply_installation_plan(plan)
        self.assertTrue((self.target / "GEMINI.md").exists())
        self.assertTrue((self.target / ".gemini" / "skills" / "security-audit" / "SKILL.md").exists())
        self.assertTrue((self.target / ".gemini" / "agents" / "security-auditor.md").exists())
        report = run_doctor(self.target)
        self.assertEqual(report["status"], "PASS")

    def test_github_copilot_adapter(self):
        plan = build_installation_plan(self.target, adapter="github-copilot", profile_id="security-audit")
        apply_installation_plan(plan)
        self.assertTrue((self.target / ".github" / "copilot-instructions.md").exists())
        self.assertTrue((self.target / ".github" / "skills" / "security-audit" / "SKILL.md").exists())
        self.assertTrue((self.target / ".github" / "agents" / "security-auditor.md").exists())
        report = run_doctor(self.target)
        self.assertEqual(report["status"], "PASS")

    def test_opencode_adapter(self):
        plan = build_installation_plan(self.target, adapter="opencode", profile_id="security-audit")
        apply_installation_plan(plan)
        self.assertTrue((self.target / "AGENTS.md").exists())
        self.assertTrue((self.target / ".opencode" / "skills" / "security-audit" / "SKILL.md").exists())
        self.assertTrue((self.target / ".opencode" / "agents" / "security-auditor.md").exists())
        report = run_doctor(self.target)
        self.assertEqual(report["status"], "PASS")

    def test_adapter_aliases_work(self):
        for alias, canonical in [("claude", "claude-code"), ("gemini", "gemini-cli"), ("copilot", "github-copilot"), ("openai-codex", "codex")]:
            plan = build_installation_plan(self.target, adapter=alias, skill_id="tdd")
            self.assertEqual(plan.adapter, canonical)


class TestConflictDetectionAndPolicies(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_unmanaged_skill_detected_as_conflict(self):
        # Simulate pre-existing unmanaged skill in target
        unmanaged_skill = self.target / ".cursor" / "skills" / "tdd" / "SKILL.md"
        unmanaged_skill.parent.mkdir(parents=True, exist_ok=True)
        unmanaged_skill.write_text("# Third Party TDD\n", encoding="utf-8")

        plan = build_installation_plan(self.target, adapter="cursor", skill_id="tdd", on_conflict="abort")
        self.assertGreater(len(plan.conflicts), 0)
        self.assertTrue(any("unmanaged" in c.lower() for c in plan.conflicts))

        # Abort policy fails apply
        with self.assertRaises(RuntimeError) as ctx:
            apply_installation_plan(plan)
        self.assertIn("conflict", str(ctx.exception).lower())

    def test_policy_keep_preserves_existing_skill(self):
        unmanaged_skill = self.target / ".cursor" / "skills" / "tdd" / "SKILL.md"
        unmanaged_skill.parent.mkdir(parents=True, exist_ok=True)
        unmanaged_skill.write_text("# Third Party TDD\n", encoding="utf-8")

        plan = build_installation_plan(self.target, adapter="cursor", skill_id="tdd", on_conflict="keep")
        self.assertEqual(len(plan.conflicts), 0)
        self.assertTrue(any("preserving" in w.lower() for w in plan.warnings))

        apply_installation_plan(plan)
        # Original content preserved
        self.assertEqual(unmanaged_skill.read_text(encoding="utf-8"), "# Third Party TDD\n")

    def test_policy_replace_creates_backup_and_overwrites(self):
        unmanaged_skill = self.target / ".cursor" / "skills" / "tdd" / "SKILL.md"
        unmanaged_skill.parent.mkdir(parents=True, exist_ok=True)
        unmanaged_skill.write_text("# Third Party TDD\n", encoding="utf-8")

        plan = build_installation_plan(self.target, adapter="cursor", skill_id="tdd", on_conflict="replace")
        self.assertEqual(len(plan.conflicts), 0)

        manifest = apply_installation_plan(plan)
        self.assertNotEqual(unmanaged_skill.read_text(encoding="utf-8"), "# Third Party TDD\n")
        self.assertGreater(len(manifest["backups"]), 0)

        # Check backup exists on disk
        backup_dir = self.target / ".agent-toolkit" / "backups"
        self.assertTrue(backup_dir.exists())
        backed_up_files = list(backup_dir.rglob("SKILL.md"))
        self.assertEqual(len(backed_up_files), 1)
        self.assertEqual(backed_up_files[0].read_text(encoding="utf-8"), "# Third Party TDD\n")

    def test_policy_rename_installs_alongside(self):
        unmanaged_skill = self.target / ".cursor" / "skills" / "tdd" / "SKILL.md"
        unmanaged_skill.parent.mkdir(parents=True, exist_ok=True)
        unmanaged_skill.write_text("# Third Party TDD\n", encoding="utf-8")

        plan = build_installation_plan(self.target, adapter="cursor", skill_id="tdd", on_conflict="rename")
        self.assertEqual(len(plan.conflicts), 0)
        self.assertEqual(plan.aliases.get("tdd"), "agent-toolkit-tdd")

        apply_installation_plan(plan)
        # Both skills co-exist
        self.assertTrue(unmanaged_skill.exists())
        self.assertEqual(unmanaged_skill.read_text(encoding="utf-8"), "# Third Party TDD\n")

        aliased_skill = self.target / ".cursor" / "skills" / "agent-toolkit-tdd" / "SKILL.md"
        self.assertTrue(aliased_skill.exists())
        self.assertIn("name: agent-toolkit-tdd", aliased_skill.read_text(encoding="utf-8"))

    def test_case_insensitive_collision_detected(self):
        unmanaged_skill = self.target / ".cursor" / "skills" / "TDD" / "SKILL.md"
        unmanaged_skill.parent.mkdir(parents=True, exist_ok=True)
        unmanaged_skill.write_text("# Upper case TDD\n", encoding="utf-8")

        plan = build_installation_plan(self.target, adapter="cursor", skill_id="tdd", on_conflict="abort")
        self.assertGreater(len(plan.conflicts), 0)

    def test_shadowed_skills_reported_by_doctor(self):
        # Install into cursor (.cursor/skills/tdd)
        plan = build_installation_plan(self.target, adapter="cursor", skill_id="tdd")
        apply_installation_plan(plan)

        # Place a conflicting unmanaged skill in secondary root (.agents/skills/tdd)
        secondary_skill = self.target / ".agents" / "skills" / "tdd" / "SKILL.md"
        secondary_skill.parent.mkdir(parents=True, exist_ok=True)
        secondary_skill.write_text("# Shadowed TDD\n", encoding="utf-8")

        report = run_doctor(self.target)
        self.assertGreater(len(report["shadowed_skills"]), 0)
        self.assertTrue(any("shadowed" in s.lower() for s in report["shadowed_skills"]))


class TestManualOnlyInvocationAcrossRuntimes(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manual_only_frontmatter_injected(self):
        for adp in ["claude-code", "cursor", "gemini-cli", "github-copilot", "opencode"]:
            target_sub = self.target / adp
            plan = build_installation_plan(target_sub, adapter=adp, skill_id="tune")
            apply_installation_plan(plan)

            # Check that installed tune SKILL.md has disable-model-invocation: true
            installed_files = list(target_sub.rglob("SKILL.md"))
            adapter_skill = [f for f in installed_files if ".agent-toolkit" not in f.parts][0]
            content = adapter_skill.read_text(encoding="utf-8")
            self.assertIn("disable-model-invocation: true", content)


if __name__ == "__main__":
    unittest.main()
