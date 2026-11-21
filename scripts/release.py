#!/usr/bin/env python3
"""
Agent Toolkit — Release Distribution Engine

Compiles, packages, validates, and indexes official repository releases
using the deterministic ZIP bundler and canonical catalog.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Please install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Ensure repository root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.bundle import (
    BUNDLE_SCHEMA_VERSION,
    bundle,
    verify_zip_archive,
)
from scripts.install import (
    ADAPTER_SPECS,
    ROOT,
    get_catalog,
    get_profiles,
    normalize_adapter,
    sha256_file,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RELEASE_INDEX_SCHEMA_VERSION = "1.0.0"
TAG_REGEX = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$")
DEFAULT_MATRIX_PATH = ROOT / "catalog" / "release-matrix.yaml"
DEFAULT_RELEASE_DIR = ROOT / "dist" / "release"


# ---------------------------------------------------------------------------
# Git Inspection & Validation
# ---------------------------------------------------------------------------

def get_git_commit(repo_root: Path = ROOT) -> str:
    """Return the 40-character HEAD commit hash, or 'unknown'."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "unknown"


def is_git_working_tree_clean(repo_root: Path = ROOT) -> bool:
    """Check if the Git working tree has zero uncommitted changes or untracked files."""
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            return not res.stdout.strip()
    except Exception:
        pass
    return False


def resolve_tag_commit(tag: str, repo_root: Path = ROOT) -> Optional[str]:
    """Resolve an existing Git tag to its commit hash, or None if tag does not exist."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", f"refs/tags/{tag}^{{commit}}"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Release Matrix Loading & Validation
# ---------------------------------------------------------------------------

def load_release_matrix(matrix_path: Path = DEFAULT_MATRIX_PATH) -> Dict[str, Any]:
    """Load the release packaging matrix YAML file."""
    if not matrix_path.exists():
        raise FileNotFoundError(f"Release matrix configuration not found at: {matrix_path}")
    try:
        data = yaml.safe_load(matrix_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"Malformed release matrix YAML in {matrix_path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Release matrix in {matrix_path} must be a dictionary.")
    return data


def validate_release_matrix(matrix_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Validate release matrix against canonical catalog and profiles.
    Returns a normalized, deduplicated list of targets:
    [{'id': id, 'type': 'skill'|'profile', 'adapter': adapter}, ...]
    """
    targets_raw = matrix_data.get("targets")
    if not isinstance(targets_raw, list) or not targets_raw:
        raise ValueError("Release matrix must contain a non-empty 'targets' list.")

    catalog = get_catalog()
    catalog_skills = {s["id"]: s for s in catalog.get("skills", []) if "id" in s}
    profiles = get_profiles()

    valid_adapters = {"canonical"} | set(ADAPTER_SPECS.keys())
    for spec in ADAPTER_SPECS.values():
        valid_adapters.update(spec.aliases)

    flat_targets: List[Dict[str, Any]] = []
    seen_identities: Set[Tuple[str, str, str]] = set()

    for idx, item in enumerate(targets_raw):
        if not isinstance(item, dict):
            raise ValueError(f"Target at index {idx} must be a dictionary.")

        item_id = item.get("id")
        item_type = item.get("type")
        adapters = item.get("adapters")

        if not item_id or not isinstance(item_id, str):
            raise ValueError(f"Target at index {idx} has invalid or missing 'id'.")
        if item_type not in ("skill", "profile"):
            raise ValueError(f"Target '{item_id}' has invalid type '{item_type}'. Must be 'skill' or 'profile'.")
        if not isinstance(adapters, list) or not adapters:
            raise ValueError(f"Target '{item_id}' must define a non-empty 'adapters' list.")

        # Validate existence in canonical registries
        if item_type == "skill":
            if item_id not in catalog_skills:
                raise ValueError(f"Release matrix specifies unknown skill '{item_id}'. Not in catalog.yaml.")
        elif item_type == "profile":
            if item_id not in profiles and item_id.lower() not in {k.lower(): k for k in profiles}:
                raise ValueError(f"Release matrix specifies unknown profile '{item_id}'. Not in profiles/.")

        for ad in adapters:
            if not isinstance(ad, str):
                raise ValueError(f"Invalid adapter '{ad}' for target '{item_id}'.")
            normalized_ad = "canonical"
            if ad.lower() != "canonical":
                try:
                    normalized_ad = normalize_adapter(ad).name
                except ValueError as exc:
                    raise ValueError(f"Unknown adapter '{ad}' for target '{item_id}': {exc}") from exc

            identity = (item_type, item_id, normalized_ad)
            if identity in seen_identities:
                raise ValueError(f"Duplicate release target defined: type={item_type}, id={item_id}, adapter={normalized_ad}")
            seen_identities.add(identity)

            flat_targets.append({
                "type": item_type,
                "id": item_id,
                "adapter": normalized_ad,
            })

    return flat_targets


# ---------------------------------------------------------------------------
# Quality Gates Runner
# ---------------------------------------------------------------------------

def run_quality_gates(repo_root: Path = ROOT) -> None:
    """
    Execute all required repository quality gates deterministically:
    1. Structural validation (validate.py)
    2. Tests suite (tests/)
    3. Scripts tests suite (scripts/tests/)
    4. Security Audit eval validator (evals/security-audit)
    """
    steps = [
        ("Structural Validation", [sys.executable, "scripts/validate.py"]),
        ("Tests Suite", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]),
        ("Scripts Tests Suite", [sys.executable, "-m", "unittest", "discover", "-s", "scripts/tests", "-p", "test_*.py"]),
        ("Security Audit Validator", [sys.executable, "-m", "unittest", "discover", "-s", "evals/security-audit", "-p", "test_*.py"]),
    ]

    for name, cmd in steps:
        res = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, check=False)
        if res.returncode != 0:
            error_output = (res.stderr.strip() or res.stdout.strip())[-1000:]
            raise RuntimeError(f"Quality gate '{name}' failed (exit {res.returncode}):\n{error_output}")


# ---------------------------------------------------------------------------
# Release Verification
# ---------------------------------------------------------------------------

def verify_release(release_dir: Path) -> Dict[str, Any]:
    """
    Independently inspects and verifies a completed release directory:
    - release-index.json exists, valid JSON, schema 1.0.0
    - All assets exist, match file size, and match sha256
    - Each ZIP archive is verified via verify_zip_archive
    - SHA256SUMS exists and matches disk contents
    """
    if not release_dir.exists():
        raise FileNotFoundError(f"Release directory does not exist: {release_dir}")

    index_path = release_dir / "release-index.json"
    if not index_path.exists():
        raise FileNotFoundError(f"Missing release-index.json in {release_dir}")

    try:
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"Malformed release-index.json: {exc}") from exc

    if not isinstance(index_data, dict):
        raise ValueError("release-index.json root must be a mapping.")
    if index_data.get("schema_version") != RELEASE_INDEX_SCHEMA_VERSION:
        raise ValueError(f"Unsupported release-index schema_version: {index_data.get('schema_version')}")

    assets = index_data.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("release-index.json must contain a non-empty 'assets' list.")

    seen_files: Set[str] = set()
    verified_assets: List[Dict[str, Any]] = []

    for idx, asset in enumerate(assets):
        if not isinstance(asset, dict):
            raise ValueError(f"Asset at index {idx} is not a mapping.")

        filename = asset.get("filename")
        expected_sha = asset.get("sha256")
        expected_size = asset.get("size_bytes")

        if not filename or not isinstance(filename, str):
            raise ValueError(f"Asset at index {idx} has invalid filename.")
        if not expected_sha or not isinstance(expected_sha, str):
            raise ValueError(f"Asset '{filename}' has invalid sha256.")
        if expected_size is None or not isinstance(expected_size, int):
            raise ValueError(f"Asset '{filename}' has invalid size_bytes.")

        if filename in seen_files:
            raise ValueError(f"Duplicate filename in release-index.json: {filename}")
        seen_files.add(filename)

        zip_path = release_dir / filename
        if not zip_path.exists():
            raise FileNotFoundError(f"Release asset file does not exist: {zip_path}")

        actual_size = zip_path.stat().st_size
        if actual_size != expected_size:
            raise ValueError(f"Asset '{filename}' size mismatch: expected {expected_size}, got {actual_size}")

        actual_sha = sha256_file(zip_path)
        if actual_sha != expected_sha:
            raise ValueError(f"Asset '{filename}' hash mismatch: expected {expected_sha}, got {actual_sha}")

        # Verify companion .sha256 file
        companion_path = release_dir / f"{filename}.sha256"
        if not companion_path.exists():
            raise FileNotFoundError(f"Missing companion checksum file: {companion_path}")
        companion_line = companion_path.read_text(encoding="utf-8").strip()
        expected_companion = f"{expected_sha}  {filename}"
        if companion_line != expected_companion:
            raise ValueError(f"Companion checksum mismatch in {companion_path.name}: expected '{expected_companion}', got '{companion_line}'")

        # Verify ZIP archive internal health, timestamps, permissions, and manifest
        verify_zip_archive(zip_path)

        verified_assets.append({
            "filename": filename,
            "type": asset.get("type"),
            "id": asset.get("id"),
            "adapter": asset.get("adapter"),
            "version": asset.get("artifact_version"),
            "sha256": actual_sha,
            "size_bytes": actual_size,
        })

    # Verify consolidated SHA256SUMS
    sums_path = release_dir / "SHA256SUMS"
    if not sums_path.exists():
        raise FileNotFoundError(f"Missing SHA256SUMS in {release_dir}")

    sums_lines = sums_path.read_text(encoding="utf-8").splitlines()
    for line in sums_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        exp_h, rel_f = parts
        target_f = release_dir / rel_f
        if not target_f.exists():
            raise FileNotFoundError(f"File in SHA256SUMS does not exist: {rel_f}")
        act_h = sha256_file(target_f)
        if act_h != exp_h:
            raise ValueError(f"SHA256SUMS hash mismatch for {rel_f}: expected {exp_h}, got {act_h}")

    return {
        "status": "PASS",
        "release_version": index_data.get("release_version"),
        "source_commit": index_data.get("source_commit"),
        "verified_asset_count": len(verified_assets),
        "assets": verified_assets,
    }


# ---------------------------------------------------------------------------
# Release Build Engine
# ---------------------------------------------------------------------------

def build_release(
    release_version: str,
    output_dir: Path,
    matrix_path: Path = DEFAULT_MATRIX_PATH,
    skip_tests: bool = False,
    force: bool = False,
    allow_dirty: bool = False,
) -> Dict[str, Any]:
    """
    Executes the release build pipeline:
    1. Validates release tag format.
    2. Validates Git commit and cleanliness.
    3. Validates release matrix against canonical catalog.
    4. Runs quality gates.
    5. Packages all targets deterministically via scripts/bundle.py.
    6. Generates release-index.json and consolidated SHA256SUMS.
    7. Verifies the complete release directory atomically.
    """
    if not TAG_REGEX.match(release_version):
        raise ValueError(
            f"Invalid release version '{release_version}'. Must follow format 'vX.Y.Z' (e.g. v0.1.0)."
        )

    # Inspect Git state
    commit_sha = get_git_commit(ROOT)
    is_clean = is_git_working_tree_clean(ROOT)

    if not is_clean and not allow_dirty:
        raise RuntimeError(
            "Working tree contains uncommitted changes or untracked files. "
            "Release builds require a clean Git working tree. Commit your changes or pass --allow-dirty for testing."
        )

    tag_commit = resolve_tag_commit(release_version, ROOT)
    if tag_commit and tag_commit != commit_sha:
        raise RuntimeError(
            f"Git tag '{release_version}' resolves to {tag_commit}, but current HEAD is {commit_sha}."
        )

    # Validate matrix
    matrix_data = load_release_matrix(matrix_path)
    flat_targets = validate_release_matrix(matrix_data)

    # Run quality gates
    if not skip_tests:
        run_quality_gates(ROOT)

    # Prepare output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    existing_items = list(output_dir.iterdir())
    if existing_items and not force:
        raise FileExistsError(
            f"Release directory '{output_dir}' already contains {len(existing_items)} item(s). Use --force to overwrite."
        )

    assets: List[Dict[str, Any]] = []

    for target in flat_targets:
        pkg_id = target["id"]
        pkg_type = target["type"]
        adapter = target["adapter"]

        if pkg_type == "skill":
            bundle_res = bundle(
                skill_id=pkg_id,
                adapter=adapter,
                output_dir=output_dir,
                force=True,
            )
        else:
            bundle_res = bundle(
                profile_id=pkg_id,
                adapter=adapter,
                output_dir=output_dir,
                force=True,
            )

        zip_file = Path(bundle_res["archive_path"])
        size_bytes = zip_file.stat().st_size
        sha256_hash = bundle_res["archive_sha256"]
        manifest = bundle_res["manifest"]

        assets.append({
            "type": pkg_type,
            "id": pkg_id,
            "artifact_version": manifest["package"]["version"],
            "adapter": manifest["target_assistant"],
            "filename": zip_file.name,
            "sha256": sha256_hash,
            "size_bytes": size_bytes,
            "verification": "structurally-verified",
            "warnings": manifest["warnings"],
        })

    # Generate release-index.json
    release_index: Dict[str, Any] = {
        "schema_version": RELEASE_INDEX_SCHEMA_VERSION,
        "repository": "Phoenixarjun/Agent-Toolkit",
        "release_version": release_version,
        "source_commit": commit_sha,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "asset_count": len(assets),
        "assets": assets,
    }

    index_path = output_dir / "release-index.json"
    index_path.write_text(json.dumps(release_index, indent=2) + "\n", encoding="utf-8")

    # Generate consolidated SHA256SUMS
    sums_lines: List[str] = [
        f"{sha256_file(index_path)}  release-index.json"
    ]
    for asset in sorted(assets, key=lambda a: a["filename"]):
        sums_lines.append(f"{asset['sha256']}  {asset['filename']}")

    sums_path = output_dir / "SHA256SUMS"
    sums_path.write_text("\n".join(sums_lines) + "\n", encoding="utf-8")

    # Verify release atomically
    verify_report = verify_release(output_dir)

    return {
        "status": "SUCCESS",
        "release_version": release_version,
        "source_commit": commit_sha,
        "release_dir": str(output_dir),
        "asset_count": len(assets),
        "index_path": str(index_path),
        "sums_path": str(sums_path),
        "assets": assets,
        "verification": verify_report,
    }


# ---------------------------------------------------------------------------
# CLI Command Handlers
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Agent Toolkit Release Distribution Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # plan
    plan_parser = subparsers.add_parser("plan", help="Preview release targets and packaging matrix")
    plan_parser.add_argument(
        "--matrix",
        default=str(DEFAULT_MATRIX_PATH),
        help="Path to release matrix configuration (default: catalog/release-matrix.yaml)",
    )
    plan_parser.add_argument("--json", action="store_true", help="Output plan as JSON")

    # build
    build_parser = subparsers.add_parser("build", help="Build a full, verified repository release")
    build_parser.add_argument(
        "--tag",
        "--version",
        dest="tag",
        required=True,
        help="Release tag version to build (e.g. v0.1.0)",
    )
    build_parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_RELEASE_DIR),
        help="Output directory for built release assets (default: dist/release/)",
    )
    build_parser.add_argument(
        "--matrix",
        default=str(DEFAULT_MATRIX_PATH),
        help="Path to release matrix configuration (default: catalog/release-matrix.yaml)",
    )
    build_parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip quality gate test execution (for testing and dry-run only)",
    )
    build_parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow building from a dirty working tree (development/testing only)",
    )
    build_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files in output-dir if present",
    )
    build_parser.add_argument("--json", action="store_true", help="Output result as JSON")

    # verify
    verify_parser = subparsers.add_parser("verify", help="Independently verify an existing release directory")
    verify_parser.add_argument(
        "--dir",
        default=str(DEFAULT_RELEASE_DIR),
        help="Path to release directory to verify (default: dist/release/)",
    )
    verify_parser.add_argument("--json", action="store_true", help="Output result as JSON")

    return parser


def cmd_plan(args: argparse.Namespace) -> int:
    try:
        matrix_data = load_release_matrix(Path(args.matrix))
        flat_targets = validate_release_matrix(matrix_data)
    except Exception as exc:
        print(f"Plan error: {exc}", file=sys.stderr)
        return 1

    commit_sha = get_git_commit(ROOT)
    is_clean = is_git_working_tree_clean(ROOT)

    plan_report = {
        "status": "PLAN_ONLY",
        "matrix_path": str(args.matrix),
        "source_commit": commit_sha,
        "working_tree_clean": is_clean,
        "target_count": len(flat_targets),
        "targets": flat_targets,
    }

    if args.json:
        print(json.dumps(plan_report, indent=2))
    else:
        print("Agent Toolkit Release Packaging Plan")
        print(f"  Matrix:       {args.matrix}")
        print(f"  Git Commit:   {commit_sha[:8] if commit_sha != 'unknown' else 'unknown'}")
        print(f"  Tree Clean:   {'YES (release-grade)' if is_clean else 'NO (development-only)'}")
        print(f"  Total Assets: {len(flat_targets)}")
        print("Configured Targets:")
        for t in flat_targets:
            print(f"  - [{t['type']}] {t['id']} -> {t['adapter']}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    try:
        res = build_release(
            release_version=args.tag,
            output_dir=Path(args.output_dir),
            matrix_path=Path(args.matrix),
            skip_tests=args.skip_tests,
            force=args.force,
            allow_dirty=args.allow_dirty,
        )
    except Exception as exc:
        print(f"Release build error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"Successfully built release {res['release_version']}")
        print(f"  Source Commit: {res['source_commit']}")
        print(f"  Output Dir:    {res['release_dir']}")
        print(f"  Total Assets:  {res['asset_count']}")
        print(f"  Release Index: {res['index_path']}")
        print(f"  Checksums:     {res['sums_path']}")
        print("Generated Assets:")
        for a in res["assets"]:
            print(f"  - {a['filename']} ({a['size_bytes']} bytes, sha256={a['sha256'][:12]}...)")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    try:
        res = verify_release(Path(args.dir))
    except Exception as exc:
        print(f"Verification error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"Release verification: PASS")
        print(f"  Release Version: {res['release_version']}")
        print(f"  Source Commit:   {res['source_commit']}")
        print(f"  Verified Assets: {res['verified_asset_count']}")
        for a in res["assets"]:
            print(f"  - {a['filename']}: OK ({a['sha256'][:12]}...)")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.subcommand == "plan":
        return cmd_plan(args)
    elif args.subcommand == "build":
        return cmd_build(args)
    elif args.subcommand == "verify":
        return cmd_verify(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
