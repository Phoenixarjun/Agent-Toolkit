#!/usr/bin/env python3
"""
Unit and integration test suite for scripts/release.py

Verifies release version parsing, release matrix validation, quality gates,
release asset packaging, release-index.json generation, atomic verification,
and byte-for-byte reproducibility across isolated environments.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts.release import (
    DEFAULT_MATRIX_PATH,
    RELEASE_INDEX_SCHEMA_VERSION,
    TAG_REGEX,
    build_release,
    load_release_matrix,
    validate_release_matrix,
    verify_release,
)
from scripts.install import ROOT, sha256_file


class TestReleaseDistributionEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="release_test_")
        self.output_dir = Path(self.temp_dir) / "release"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_version_format_validation(self) -> None:
        """Verify that TAG_REGEX strictly enforces SemVer with leading v."""
        valid_tags = ["v0.1.0", "v1.0.0", "v2.3.4", "v1.0.0-rc.1", "v0.0.1-beta"]
        invalid_tags = ["0.1.0", "v1", "v1.0", "release-1.0", "latest", "v1.0.0.0", ""]

        for tag in valid_tags:
            self.assertIsNotNone(TAG_REGEX.match(tag), f"Expected valid tag: {tag}")

        for tag in invalid_tags:
            self.assertIsNone(TAG_REGEX.match(tag), f"Expected invalid tag: {tag}")

    def test_canonical_matrix_validation(self) -> None:
        """Verify that the repository release-matrix.yaml validates cleanly."""
        matrix_data = load_release_matrix(DEFAULT_MATRIX_PATH)
        flat_targets = validate_release_matrix(matrix_data)
        self.assertGreaterEqual(len(flat_targets), 10)

        # Check expected core capabilities are present
        target_ids = {t["id"] for t in flat_targets}
        self.assertIn("code-review", target_ids)
        self.assertIn("security-audit", target_ids)
        self.assertIn("ui-ux", target_ids)
        self.assertIn("software-engineering", target_ids)

    def test_matrix_rejects_unknown_skill(self) -> None:
        """Verify that unknown skills are rejected during matrix validation."""
        bad_matrix = {
            "schema_version": "1.0.0",
            "targets": [{"id": "non-existent-skill", "type": "skill", "adapters": ["canonical"]}],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_release_matrix(bad_matrix)
        self.assertIn("unknown skill", str(ctx.exception))

    def test_matrix_rejects_unknown_profile(self) -> None:
        """Verify that unknown profiles are rejected during matrix validation."""
        bad_matrix = {
            "schema_version": "1.0.0",
            "targets": [{"id": "non-existent-profile", "type": "profile", "adapters": ["canonical"]}],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_release_matrix(bad_matrix)
        self.assertIn("unknown profile", str(ctx.exception))

    def test_matrix_rejects_unknown_adapter(self) -> None:
        """Verify that unknown adapters are rejected during matrix validation."""
        bad_matrix = {
            "schema_version": "1.0.0",
            "targets": [{"id": "code-review", "type": "skill", "adapters": ["invalid-adapter"]}],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_release_matrix(bad_matrix)
        self.assertIn("Unknown adapter", str(ctx.exception))

    def test_matrix_rejects_duplicate_targets(self) -> None:
        """Verify that duplicate targets are rejected during matrix validation."""
        duplicate_matrix = {
            "schema_version": "1.0.0",
            "targets": [
                {"id": "code-review", "type": "skill", "adapters": ["canonical"]},
                {"id": "code-review", "type": "skill", "adapters": ["canonical"]},
            ],
        }
        with self.assertRaises(ValueError) as ctx:
            validate_release_matrix(duplicate_matrix)
        self.assertIn("Duplicate release target defined", str(ctx.exception))

    def test_build_release_with_focused_matrix(self) -> None:
        """Test building a release with a focused custom matrix and verifying release-index.json."""
        custom_matrix_path = Path(self.temp_dir) / "test-matrix.yaml"
        custom_matrix_path.write_text(
            """
schema_version: "1.0.0"
targets:
  - id: "code-review"
    type: "skill"
    adapters:
      - "canonical"
      - "claude-code"
  - id: "ui-ux"
    type: "profile"
    adapters:
      - "canonical"
""",
            encoding="utf-8",
        )

        res = build_release(
            release_version="v0.1.0",
            output_dir=self.output_dir,
            matrix_path=custom_matrix_path,
            skip_tests=True,
            force=True,
            allow_dirty=True,
        )

        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["release_version"], "v0.1.0")
        self.assertEqual(res["asset_count"], 3)

        # Inspect release-index.json
        index_file = self.output_dir / "release-index.json"
        self.assertTrue(index_file.exists())
        index_data = json.loads(index_file.read_text(encoding="utf-8"))
        self.assertEqual(index_data["schema_version"], RELEASE_INDEX_SCHEMA_VERSION)
        self.assertEqual(index_data["release_version"], "v0.1.0")
        self.assertEqual(index_data["repository"], "Phoenixarjun/Agent-Toolkit")
        self.assertEqual(len(index_data["assets"]), 3)

        # Inspect SHA256SUMS
        sums_file = self.output_dir / "SHA256SUMS"
        self.assertTrue(sums_file.exists())
        sums_text = sums_file.read_text(encoding="utf-8")
        self.assertIn("release-index.json", sums_text)
        self.assertIn("code-review-1.2.0-canonical.zip", sums_text)
        self.assertIn("code-review-1.2.0-claude-code.zip", sums_text)
        self.assertIn("ui-ux-1.0.0-canonical.zip", sums_text)

        # Verify release directory
        v_res = verify_release(self.output_dir)
        self.assertEqual(v_res["status"], "PASS")
        self.assertEqual(v_res["verified_asset_count"], 3)

    def test_build_release_reproducibility(self) -> None:
        """Verify that building the same release twice yields identical assets and hashes."""
        custom_matrix_path = Path(self.temp_dir) / "test-matrix.yaml"
        custom_matrix_path.write_text(
            """
schema_version: "1.0.0"
targets:
  - id: "code-review"
    type: "skill"
    adapters:
      - "canonical"
""",
            encoding="utf-8",
        )

        out1 = Path(self.temp_dir) / "out1"
        out2 = Path(self.temp_dir) / "out2"
        out1.mkdir()
        out2.mkdir()

        res1 = build_release(
            release_version="v0.1.0",
            output_dir=out1,
            matrix_path=custom_matrix_path,
            skip_tests=True,
            force=True,
            allow_dirty=True,
        )
        res2 = build_release(
            release_version="v0.1.0",
            output_dir=out2,
            matrix_path=custom_matrix_path,
            skip_tests=True,
            force=True,
            allow_dirty=True,
        )

        self.assertEqual(res1["assets"][0]["sha256"], res2["assets"][0]["sha256"])
        zip1_path = out1 / res1["assets"][0]["filename"]
        zip2_path = out2 / res2["assets"][0]["filename"]
        self.assertEqual(sha256_file(zip1_path), sha256_file(zip2_path))

    def test_verify_release_detects_tampered_asset(self) -> None:
        """Verify that verify_release detects if a release zip was modified or tampered with."""
        custom_matrix_path = Path(self.temp_dir) / "test-matrix.yaml"
        custom_matrix_path.write_text(
            """
schema_version: "1.0.0"
targets:
  - id: "code-review"
    type: "skill"
    adapters:
      - "canonical"
""",
            encoding="utf-8",
        )

        build_release(
            release_version="v0.1.0",
            output_dir=self.output_dir,
            matrix_path=custom_matrix_path,
            skip_tests=True,
            force=True,
            allow_dirty=True,
        )

        # Tamper with the zip file
        zip_file = next(self.output_dir.glob("*.zip"))
        raw = bytearray(zip_file.read_bytes())
        raw[-20:] = b"CORRUPTED_RELEASE_XX"
        zip_file.write_bytes(raw)

        with self.assertRaises(ValueError) as ctx:
            verify_release(self.output_dir)
        self.assertIn("hash mismatch", str(ctx.exception).lower())

    def test_verify_release_detects_missing_index(self) -> None:
        """Verify that verify_release fails if release-index.json is missing."""
        with self.assertRaises(FileNotFoundError):
            verify_release(self.output_dir)

    def test_dirty_working_tree_rejected_without_allow_dirty(self) -> None:
        """Verify that build_release rejects dirty working tree when allow_dirty=False."""
        with patch("scripts.release.is_git_working_tree_clean", return_value=False):
            with self.assertRaises(RuntimeError) as ctx:
                build_release(
                    release_version="v0.1.0",
                    output_dir=self.output_dir,
                    skip_tests=True,
                    allow_dirty=False,
                )
            self.assertIn("Working tree contains uncommitted changes", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
