#!/usr/bin/env python3
"""
Unit and integration test suite for scripts/bundle.py

Verifies deterministic packaging, reproducible byte-identical ZIP creation,
safe staging, dependency closure completeness, trust boundary warnings,
optional dependency handling, and archive extraction integrity.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.bundle import (
    BUNDLE_SCHEMA_VERSION,
    FIXED_ZIP_TIMESTAMP,
    SECURITY_AUDIT_ASSURANCE_WARNING,
    bundle,
    create_deterministic_zip,
    get_git_status_and_commit,
    stage_bundle,
    verify_zip_archive,
)
from scripts.install import ROOT, sha256_file


class TestBundleEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="bundle_test_")
        self.output_dir = Path(self.temp_dir) / "dist"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_plan_standalone_skill(self) -> None:
        """Test planning a standalone skill without generating an archive."""
        res = bundle(skill_id="code-review", adapter="canonical", dry_run=True)
        self.assertEqual(res["status"], "PLAN_ONLY")
        self.assertEqual(res["package"]["name"], "code-review")
        self.assertEqual(res["package"]["type"], "skill")
        self.assertEqual(res["target_assistant"], "canonical")
        self.assertIn("code-review", [a["id"] for a in res["artifacts"]])
        self.assertEqual(list(self.output_dir.glob("*.zip")), [])

    def test_plan_composed_profile(self) -> None:
        """Test planning a composed profile (ui-ux) without generating an archive."""
        res = bundle(profile_id="ui-ux", adapter="canonical", dry_run=True)
        self.assertEqual(res["status"], "PLAN_ONLY")
        self.assertEqual(res["package"]["name"], "ui-ux")
        self.assertEqual(res["package"]["type"], "profile")
        art_ids = [a["id"] for a in res["artifacts"]]
        self.assertIn("ui-ux-design", art_ids)
        self.assertIn("ui-critic", art_ids)
        self.assertIn("ui-design-build-review", art_ids)

    def test_build_standalone_skill_canonical(self) -> None:
        """Test building a canonical package for code-review."""
        res = bundle(
            skill_id="code-review",
            adapter="canonical",
            output_dir=self.output_dir,
            force=True,
        )
        self.assertEqual(res["status"], "SUCCESS")
        zip_path = Path(res["archive_path"])
        chk_path = Path(res["checksum_path"])

        self.assertTrue(zip_path.exists())
        self.assertTrue(chk_path.exists())
        self.assertEqual(chk_path.name, f"{zip_path.name}.sha256")

        # Verify companion checksum file matches zip hash
        checksum_content = chk_path.read_text(encoding="utf-8").strip()
        expected_line = f"{res['archive_sha256']}  {zip_path.name}"
        self.assertEqual(checksum_content, expected_line)

    def test_build_composed_profile_vendor_adapter(self) -> None:
        """Test building a vendor-specific profile bundle (ui-ux for claude-code)."""
        res = bundle(
            profile_id="ui-ux",
            adapter="claude",
            output_dir=self.output_dir,
            force=True,
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["manifest"]["target_assistant"], "claude-code")

        # Verify extracted contents contain adapter entrypoint and skills
        with zipfile.ZipFile(res["archive_path"], "r") as zf:
            namelist = zf.namelist()
            self.assertIn("payload/CLAUDE.md", namelist)
            self.assertIn("payload/.claude/agents/ui-critic.md", namelist)
            self.assertIn("payload/.claude/skills/ui-ux-design/SKILL.md", namelist)

    def test_build_security_audit_preserves_trust_boundaries(self) -> None:
        """Test that security-audit package includes execution assurance warnings."""
        res = bundle(
            skill_id="security-audit",
            adapter="canonical",
            output_dir=self.output_dir,
            force=True,
        )
        self.assertEqual(res["status"], "SUCCESS")
        manifest = res["manifest"]
        self.assertTrue(any("security-audit workflow is statically anchored" in w for w in manifest["warnings"]))

        # Inspect INSTALL.md inside the archive
        with zipfile.ZipFile(res["archive_path"], "r") as zf:
            install_md = zf.read("INSTALL.md").decode("utf-8")
            self.assertIn("isolated execution environment for multi-agent assurance", install_md)
            self.assertIn(".agent-toolkit/workflows/security-audit/WORKFLOW.md", install_md)

    def test_deterministic_reproducible_byte_identical_archives(self) -> None:
        """Test that building the same package twice yields the exact same SHA-256."""
        dir1 = Path(self.temp_dir) / "dist1"
        dir2 = Path(self.temp_dir) / "dist2"
        dir1.mkdir()
        dir2.mkdir()

        res1 = bundle(skill_id="code-review", adapter="canonical", output_dir=dir1)
        res2 = bundle(skill_id="code-review", adapter="canonical", output_dir=dir2)

        self.assertEqual(res1["archive_sha256"], res2["archive_sha256"])
        self.assertEqual(
            sha256_file(Path(res1["archive_path"])),
            sha256_file(Path(res2["archive_path"])),
        )

    def test_deterministic_reproducible_profile_archives(self) -> None:
        """Test byte-identical reproducibility on a complex composed profile."""
        dir1 = Path(self.temp_dir) / "dist1"
        dir2 = Path(self.temp_dir) / "dist2"
        dir1.mkdir()
        dir2.mkdir()

        res1 = bundle(profile_id="ui-ux", adapter="cursor", output_dir=dir1)
        res2 = bundle(profile_id="ui-ux", adapter="cursor", output_dir=dir2)

        self.assertEqual(res1["archive_sha256"], res2["archive_sha256"])

    def test_optional_dependencies_inclusion(self) -> None:
        """Test that optional dependencies are excluded by default and included with --all-optional."""
        res_default = bundle(skill_id="teach", adapter="canonical", dry_run=True)
        default_art_ids = [a["id"] for a in res_default["artifacts"]]
        self.assertNotIn("research", default_art_ids)

        res_optional = bundle(skill_id="teach", adapter="canonical", all_optional=True, dry_run=True)
        opt_art_ids = [a["id"] for a in res_optional["artifacts"]]
        self.assertIn("research", opt_art_ids)

    def test_manifest_is_non_self_referential(self) -> None:
        """Verify that bundle-manifest.json does NOT contain its own hash in file_hashes."""
        res = bundle(skill_id="code-review", adapter="canonical", output_dir=self.output_dir, force=True)
        manifest = res["manifest"]
        file_hashes = manifest["file_hashes"]
        self.assertNotIn("bundle-manifest.json", file_hashes)
        self.assertIn("INSTALL.md", file_hashes)
        self.assertTrue(any(k.startswith("payload/") for k in file_hashes))

    def test_force_flag_prevents_accidental_overwrite(self) -> None:
        """Verify that bundling fails if archive exists and force=False, but succeeds with force=True."""
        bundle(skill_id="code-review", adapter="canonical", output_dir=self.output_dir)
        with self.assertRaises(FileExistsError):
            bundle(skill_id="code-review", adapter="canonical", output_dir=self.output_dir, force=False)

        res = bundle(skill_id="code-review", adapter="canonical", output_dir=self.output_dir, force=True)
        self.assertEqual(res["status"], "SUCCESS")

    def test_archive_fixed_timestamps_and_permissions(self) -> None:
        """Verify that all entries in the ZIP archive have fixed epoch and normalized permissions."""
        res = bundle(skill_id="code-review", adapter="canonical", output_dir=self.output_dir, force=True)
        with zipfile.ZipFile(res["archive_path"], "r") as zf:
            for info in zf.infolist():
                self.assertEqual(info.date_time, FIXED_ZIP_TIMESTAMP)
                # Check permissions (high 16 bits of external_attr)
                perm = info.external_attr >> 16
                if info.is_dir():
                    self.assertEqual(perm & 0o777, 0o755)
                else:
                    self.assertEqual(perm & 0o777, 0o644)

    def test_corrupted_archive_rejected_by_verifier(self) -> None:
        """Verify that verify_zip_archive detects file corruption."""
        res = bundle(skill_id="code-review", adapter="canonical", output_dir=self.output_dir, force=True)
        zip_path = Path(res["archive_path"])

        # Corrupt the zip file
        raw = bytearray(zip_path.read_bytes())
        raw[-20:] = b"CORRUPTED_BYTES_HERE"
        corrupt_zip = zip_path.with_name("corrupt.zip")
        corrupt_zip.write_bytes(raw)

        with self.assertRaises(Exception):
            verify_zip_archive(corrupt_zip)

    def test_path_traversal_in_archive_rejected(self) -> None:
        """Verify that verify_zip_archive detects and rejects path traversal in entries."""
        bad_zip = self.output_dir / "bad_traversal.zip"
        with zipfile.ZipFile(bad_zip, "w") as zf:
            zi = zipfile.ZipInfo("../escape.txt", FIXED_ZIP_TIMESTAMP)
            zf.writestr(zi, b"malicious content")

        with self.assertRaises(ValueError) as ctx:
            verify_zip_archive(bad_zip)
        self.assertIn("Unsafe file path inside ZIP archive", str(ctx.exception))

    def test_drive_qualified_in_archive_rejected(self) -> None:
        """Verify that verify_zip_archive detects and rejects drive-qualified entries."""
        bad_zip = self.output_dir / "bad_drive.zip"
        with zipfile.ZipFile(bad_zip, "w") as zf:
            zi = zipfile.ZipInfo("C:escape.txt", FIXED_ZIP_TIMESTAMP)
            zf.writestr(zi, b"malicious content")

        with self.assertRaises(ValueError) as ctx:
            verify_zip_archive(bad_zip)
        self.assertIn("Unsafe file path inside ZIP archive", str(ctx.exception))

    def test_hash_mismatch_in_manifest_rejected(self) -> None:
        """Verify that verify_zip_archive detects if an extracted file does not match manifest hash."""
        res = bundle(skill_id="code-review", adapter="canonical", output_dir=self.output_dir, force=True)
        zip_path = Path(res["archive_path"])

        # Create tampered archive where a file's content is changed
        tampered_zip = self.output_dir / "tampered.zip"
        with zipfile.ZipFile(zip_path, "r") as src_zf, zipfile.ZipFile(tampered_zip, "w") as dst_zf:
            for item in src_zf.infolist():
                content = src_zf.read(item.filename)
                if item.filename == "INSTALL.md":
                    content = b"# TAMPERED INSTALL GUIDE"
                dst_zf.writestr(item, content)

        with self.assertRaises(RuntimeError) as ctx:
            verify_zip_archive(tampered_zip)
        self.assertIn("Hash mismatch in archive file", str(ctx.exception))

    def test_invalid_targets_fail_cleanly(self) -> None:
        """Verify that invalid skill, profile, or combination raises ValueError."""
        with self.assertRaises(ValueError):
            bundle(skill_id="non-existent-skill", adapter="canonical")

        with self.assertRaises(ValueError):
            bundle(profile_id="non-existent-profile", adapter="canonical")

        with self.assertRaises(ValueError):
            bundle(skill_id="code-review", profile_id="ui-ux")

        with self.assertRaises(ValueError):
            bundle()


if __name__ == "__main__":
    unittest.main()
