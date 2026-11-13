#!/usr/bin/env python3
"""
Agent Toolkit — Deterministic ZIP Packaging Engine

Produces reproducible, cryptographically validated ZIP archives for skills
and composed profiles, targeted either for canonical distribution or specific
coding assistants.

Reuses the catalog, dependency resolver, and installer staging engine from
scripts.install without duplicating them.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure repository root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.install import (
    ADAPTER_SPECS,
    ROOT,
    InstallationPlan,
    PlanFile,
    ResolvedArtifact,
    apply_installation_plan,
    build_installation_plan,
    ensure_safe_relative_path,
    get_catalog,
    get_profiles,
    is_symlink_or_junction,
    normalize_adapter,
    resolve_dependencies,
    run_doctor,
    sha256_content,
    sha256_file,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BUNDLE_SCHEMA_VERSION = "1.0.0"
FIXED_ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)
FIXED_ISO_TIMESTAMP = "2026-01-01T00:00:00+00:00"
FILE_PERMISSIONS = (0o644 | stat.S_IFREG) << 16
DIR_PERMISSIONS = (0o755 | stat.S_IFDIR) << 16

SECURITY_AUDIT_ASSURANCE_WARNING = (
    "security-audit workflow is statically anchored to "
    ".agent-toolkit/workflows/security-audit/WORKFLOW.md and requires an "
    "isolated execution environment for multi-agent assurance."
)


# ---------------------------------------------------------------------------
# Git & Environment Inspection
# ---------------------------------------------------------------------------

def get_git_status_and_commit(repo_root: Path = ROOT) -> Tuple[str, str]:
    """
    Inspect the Git repository to determine build mode ('release' vs 'development')
    and the current HEAD commit hash.
    """
    commit_sha = "unknown"
    build_mode = "development"

    try:
        rev_res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if rev_res.returncode == 0:
            commit_sha = rev_res.stdout.strip()
    except Exception:
        pass

    try:
        status_res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if status_res.returncode == 0:
            porcelain_output = status_res.stdout.strip()
            if not porcelain_output and commit_sha != "unknown":
                build_mode = "release"
            else:
                build_mode = "development"
    except Exception:
        build_mode = "development"

    return build_mode, commit_sha


# ---------------------------------------------------------------------------
# Canonical Installation Plan Construction
# ---------------------------------------------------------------------------

def build_canonical_plan(
    target_dir: Path,
    profile_id: Optional[str] = None,
    skill_id: Optional[str] = None,
    selected_optionals: Optional[Set[str]] = None,
    all_optional: bool = False,
) -> InstallationPlan:
    """
    Builds an installation plan for canonical packaging, copying canonical
    artifacts into .agent-toolkit/ without vendor-specific adapter files.
    """
    catalog = get_catalog()
    profile_data = None
    if profile_id:
        profiles = get_profiles()
        profile_data = profiles.get(profile_id)
        if not profile_data:
            for p_name, p_data in profiles.items():
                if p_name.lower() == profile_id.lower():
                    profile_data = p_data
                    profile_id = p_name
                    break
        if not profile_data:
            raise ValueError(f"Profile not found: {profile_id}. Available: {', '.join(profiles.keys())}")

    artifacts, opt_inc, opt_skip, opt_unavail = resolve_dependencies(
        catalog=catalog,
        profile_data=profile_data,
        skill_id=skill_id,
        selected_optionals=selected_optionals,
        all_optional=all_optional,
    )

    plan = InstallationPlan(
        target_dir=target_dir,
        adapter="canonical",
        profile_id=profile_id,
        skill_id=skill_id,
        artifacts=artifacts,
        optional_included=opt_inc,
        optional_skipped=opt_skip,
        optional_unavailable=opt_unavail,
        on_conflict="replace",
    )

    for art in artifacts:
        src_path = ROOT / art.canonical_path
        if src_path.is_file():
            dest_rel = f".agent-toolkit/{art.canonical_path}"
            plan.files.append(PlanFile(rel_destination=dest_rel, source_path=art.canonical_path))
        elif src_path.is_dir():
            for file_path in src_path.rglob("*"):
                if file_path.is_file():
                    rel_to_root = file_path.relative_to(ROOT).as_posix()
                    dest_rel = f".agent-toolkit/{rel_to_root}"
                    plan.files.append(PlanFile(rel_destination=dest_rel, source_path=rel_to_root))

    pref_source = "templates/documents/ENGINEERING-PREFERENCES.md"
    pref_dest = ".agent-toolkit/ENGINEERING-PREFERENCES.md"
    if (ROOT / pref_source).exists():
        plan.files.append(PlanFile(rel_destination=pref_dest, source_path=pref_source))

    if any(a.id == "code-explore" for a in artifacts):
        val_source = "scripts/validate_code_exploration.py"
        if (ROOT / val_source).exists():
            plan.files.append(PlanFile(rel_destination=f".agent-toolkit/{val_source}", source_path=val_source))

    if any(a.id == "code" for a in artifacts):
        val_source = "scripts/validate_code_implementation.py"
        if (ROOT / val_source).exists():
            plan.files.append(PlanFile(rel_destination=f".agent-toolkit/{val_source}", source_path=val_source))

    if any(a.id == "security-audit" for a in artifacts):
        plan.warnings.append(SECURITY_AUDIT_ASSURANCE_WARNING)

    return plan


# ---------------------------------------------------------------------------
# Installation Guide Generation
# ---------------------------------------------------------------------------

def generate_install_guide(
    package_name: str,
    package_version: str,
    target_assistant: str,
    build_mode: str,
    git_commit: str,
    archive_filename: str,
    artifacts: List[ResolvedArtifact],
    warnings: List[str],
) -> str:
    """
    Generates INSTALL.md documenting inspection, extraction, and trust boundaries.
    """
    artifacts_rows = []
    for art in artifacts:
        artifacts_rows.append(f"- **{art.id}** ({art.group}) — `{art.canonical_path}` (v{art.version})")
    artifacts_text = "\n".join(artifacts_rows)

    warnings_text = ""
    if warnings:
        warnings_lines = ["\n## Security & Runtime Assurance Notices\n"]
        for w in warnings:
            warnings_lines.append(f"> [!WARNING]\n> {w}\n")
        warnings_text = "\n".join(warnings_lines)

    guide = f"""# Agent Toolkit Package: {package_name} v{package_version}

- **Target Assistant**: {target_assistant}
- **Build Mode**: {build_mode}
- **Git Commit**: `{git_commit}`
- **Package Schema**: {BUNDLE_SCHEMA_VERSION}

## Package Structure

This package is a deterministic, self-verifying bundle containing:
- `bundle-manifest.json`: Dependency closure metadata, build metadata, and cryptographic file hashes.
- `SHA256SUMS`: Standalone verification checksums for every file in this package.
- `INSTALL.md`: This installation and verification guide.
- `payload/`: Ready-to-use artifacts pre-configured for `{target_assistant}`.

### Included Artifacts
{artifacts_text}

## Pre-Installation Verification

Before extracting or applying this package, verify its integrity:

1. Verify archive checksum:
   ```bash
   sha256sum -c {archive_filename}.sha256
   ```

2. Inspect package manifest:
   ```bash
   cat bundle-manifest.json
   ```

3. Verify all extracted files against SHA256SUMS:
   ```bash
   sha256sum -c SHA256SUMS
   ```

## Safe Installation Instructions

> [!CAUTION]
> **Do not perform blind overwrites**. Always inspect existing project files and
> back up uncommitted work before copying payload contents into your workspace.

To install into your target project:

### POSIX (Linux / macOS)
```bash
cp -R payload/* /path/to/your/project/
```

### Windows (PowerShell)
```powershell
Copy-Item -Path "payload\\*" -Destination "C:\\path\\to\\your\\project" -Recurse
```

After copying, the `.agent-toolkit/manifest.json` file inside your project tracks
all installed files and allows running integrity checks via `python scripts/install.py doctor --into .`.
{warnings_text}
"""
    return guide


# ---------------------------------------------------------------------------
# Isolated Staging and Manifest Generation
# ---------------------------------------------------------------------------

def stage_bundle(
    staging_root: Path,
    profile_id: Optional[str] = None,
    skill_id: Optional[str] = None,
    adapter: str = "canonical",
    selected_optionals: Optional[Set[str]] = None,
    all_optional: bool = False,
) -> Tuple[Path, Dict[str, Any], InstallationPlan]:
    """
    Stages the package in an isolated directory, runs doctor verification,
    and produces bundle-manifest.json, INSTALL.md, and SHA256SUMS.
    """
    stage_dir = staging_root / "stage"
    payload_dir = stage_dir / "payload"
    stage_dir.mkdir(parents=True, exist_ok=True)
    payload_dir.mkdir(parents=True, exist_ok=True)

    normalized_adapter_name = "canonical"
    if adapter.lower() != "canonical":
        spec = normalize_adapter(adapter)
        normalized_adapter_name = spec.name
        plan = build_installation_plan(
            target_dir=payload_dir,
            adapter=normalized_adapter_name,
            profile_id=profile_id,
            skill_id=skill_id,
            selected_optionals=selected_optionals,
            all_optional=all_optional,
            on_conflict="replace",
        )
    else:
        plan = build_canonical_plan(
            target_dir=payload_dir,
            profile_id=profile_id,
            skill_id=skill_id,
            selected_optionals=selected_optionals,
            all_optional=all_optional,
        )

    # Apply plan into payload directory
    apply_installation_plan(plan, force=True)

    # Normalize installed_at in .agent-toolkit/manifest.json for deterministic packaging
    installed_manifest_path = payload_dir / ".agent-toolkit" / "manifest.json"
    if installed_manifest_path.exists():
        try:
            mf_content = json.loads(installed_manifest_path.read_text(encoding="utf-8"))
            mf_content["installed_at"] = FIXED_ISO_TIMESTAMP
            installed_manifest_path.write_text(json.dumps(mf_content, indent=2) + "\n", encoding="utf-8")
        except Exception:
            pass

    # Run doctor verification on staged payload
    doctor_res = run_doctor(payload_dir)
    if doctor_res["status"] != "PASS":
        errors = "; ".join(doctor_res["errors"])
        raise RuntimeError(f"Staged payload failed doctor verification: {errors}")

    # Inspect git repo state
    build_mode, git_commit = get_git_status_and_commit(ROOT)

    # Resolve package name and version
    catalog = get_catalog()
    package_name = profile_id or skill_id or "bundle"
    package_type = "profile" if profile_id else "skill"
    package_version = "1.0.0"

    if skill_id:
        skill_entry = next((s for s in catalog.get("skills", []) if s.get("id") == skill_id), None)
        if skill_entry and skill_entry.get("version"):
            package_version = str(skill_entry["version"])
    elif profile_id:
        profiles = get_profiles()
        p_data = profiles.get(profile_id, {})
        if p_data.get("version"):
            package_version = str(p_data["version"])

    archive_filename = f"{package_name}-{package_version}-{normalized_adapter_name}.zip"

    # Consolidate warnings
    warnings: List[str] = list(plan.warnings)
    if any(a.id == "security-audit" for a in plan.artifacts):
        if SECURITY_AUDIT_ASSURANCE_WARNING not in warnings:
            warnings.append(SECURITY_AUDIT_ASSURANCE_WARNING)

    # Compute hashes for all payload files (relative to stage_dir, using POSIX slashes)
    file_hashes: Dict[str, str] = {}
    for f in sorted(payload_dir.rglob("*")):
        if f.is_file():
            rel_p = f.relative_to(stage_dir).as_posix()
            file_hashes[rel_p] = sha256_file(f)

    # Generate and write INSTALL.md
    install_guide_content = generate_install_guide(
        package_name=package_name,
        package_version=package_version,
        target_assistant=normalized_adapter_name,
        build_mode=build_mode,
        git_commit=git_commit,
        archive_filename=archive_filename,
        artifacts=plan.artifacts,
        warnings=warnings,
    )
    install_md_path = stage_dir / "INSTALL.md"
    install_md_path.write_text(install_guide_content, encoding="utf-8")
    file_hashes["INSTALL.md"] = sha256_file(install_md_path)

    # Build bundle-manifest.json
    # CRITICAL: bundle-manifest.json is NOT included in file_hashes to prevent self-reference!
    manifest_data: Dict[str, Any] = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "package": {
            "name": package_name,
            "version": package_version,
            "type": package_type,
        },
        "build_mode": build_mode,
        "git_commit": git_commit,
        "target_assistant": normalized_adapter_name,
        "artifacts": [
            {
                "group": a.group,
                "id": a.id,
                "version": a.version,
                "canonical_path": a.canonical_path,
            }
            for a in plan.artifacts
        ],
        "required_dependencies": [a.id for a in plan.artifacts],
        "optional_dependencies_included": plan.optional_included,
        "optional_dependencies_available": plan.optional_skipped + plan.optional_unavailable,
        "verification_status": "verified",
        "warnings": warnings,
        "file_hashes": file_hashes,
    }

    manifest_json_path = stage_dir / "bundle-manifest.json"
    manifest_json_text = json.dumps(manifest_data, indent=2) + "\n"
    manifest_json_path.write_text(manifest_json_text, encoding="utf-8")

    # Generate SHA256SUMS for the whole package
    manifest_hash = sha256_file(manifest_json_path)
    sha256sums_lines: List[str] = [
        f"{manifest_hash}  bundle-manifest.json",
        f"{file_hashes['INSTALL.md']}  INSTALL.md",
    ]
    for rel_f in sorted(file_hashes.keys()):
        if rel_f != "INSTALL.md":
            sha256sums_lines.append(f"{file_hashes[rel_f]}  {rel_f}")

    sha256sums_content = "\n".join(sha256sums_lines) + "\n"
    (stage_dir / "SHA256SUMS").write_text(sha256sums_content, encoding="utf-8")

    return stage_dir, manifest_data, plan


# ---------------------------------------------------------------------------
# Deterministic ZIP Packaging Engine
# ---------------------------------------------------------------------------

def create_deterministic_zip(stage_dir: Path, output_zip_path: Path) -> str:
    """
    Creates a deterministic, byte-for-byte reproducible ZIP archive from stage_dir.
    Normalizes timestamps, permissions, entry sorting, and POSIX path separators.
    """
    output_zip_path.parent.mkdir(parents=True, exist_ok=True)
    temp_zip_path = output_zip_path.with_name(f"{output_zip_path.name}.tmp")

    # Discover and sort all directory and file paths relative to stage_dir
    all_dirs: Set[str] = set()
    all_files: List[Tuple[str, Path]] = []

    for item in stage_dir.rglob("*"):
        rel_posix = item.relative_to(stage_dir).as_posix()
        # Security validation on paths
        if rel_posix.startswith(("/", "\\")) or ".." in rel_posix or re.match(r"^[a-zA-Z]:", rel_posix):
            raise ValueError(f"Unsafe path encountered during packaging: {rel_posix}")

        if item.is_dir():
            all_dirs.add(rel_posix)
        elif item.is_file():
            # Add all parent directories
            parent = item.parent
            while parent != stage_dir:
                all_dirs.add(parent.relative_to(stage_dir).as_posix())
                parent = parent.parent
            all_files.append((rel_posix, item))

    sorted_dirs = sorted(list(all_dirs))
    sorted_files = sorted(all_files, key=lambda x: x[0])

    if temp_zip_path.exists():
        temp_zip_path.unlink()

    with zipfile.ZipFile(temp_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Write directory entries first
        for d in sorted_dirs:
            zinfo = zipfile.ZipInfo(f"{d}/", FIXED_ZIP_TIMESTAMP)
            zinfo.external_attr = DIR_PERMISSIONS
            zf.writestr(zinfo, b"")

        # Write file entries sorted
        for rel_name, file_path in sorted_files:
            file_bytes = file_path.read_bytes()
            zinfo = zipfile.ZipInfo(rel_name, FIXED_ZIP_TIMESTAMP)
            zinfo.external_attr = FILE_PERMISSIONS
            zf.writestr(zinfo, file_bytes)

    # Atomic move
    if output_zip_path.exists():
        output_zip_path.unlink()
    temp_zip_path.replace(output_zip_path)

    return sha256_file(output_zip_path)


# ---------------------------------------------------------------------------
# Archive Extraction Verification
# ---------------------------------------------------------------------------

def verify_zip_archive(zip_path: Path) -> None:
    """
    Verifies that a generated ZIP archive is healthy, has no directory traversal,
    and every file matches its hash in bundle-manifest.json and SHA256SUMS.
    """
    if not zip_path.exists():
        raise FileNotFoundError(f"Archive not found: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as zf:
        test_res = zf.testzip()
        if test_res is not None:
            raise RuntimeError(f"ZIP corrupted: error in {test_res}")

        # Check path safety and fixed timestamps
        for info in zf.infolist():
            fname = info.filename
            if fname.startswith(("/", "\\")) or ".." in fname or re.match(r"^[a-zA-Z]:", fname):
                raise ValueError(f"Unsafe file path inside ZIP archive: {fname}")
            if info.date_time != FIXED_ZIP_TIMESTAMP:
                raise ValueError(f"Non-deterministic timestamp in ZIP entry {fname}: {info.date_time}")

    with tempfile.TemporaryDirectory() as td:
        extract_root = Path(td)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_root)

        manifest_path = extract_root / "bundle-manifest.json"
        if not manifest_path.exists():
            raise RuntimeError("Missing bundle-manifest.json in extracted archive")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if "bundle-manifest.json" in manifest.get("file_hashes", {}):
            raise ValueError("Manifest is self-referential: contains its own hash")

        file_hashes = manifest.get("file_hashes", {})
        for rel_path, expected_hash in file_hashes.items():
            fpath = extract_root / rel_path
            if not fpath.exists():
                raise RuntimeError(f"Missing file in archive according to manifest: {rel_path}")
            actual_hash = sha256_file(fpath)
            if actual_hash != expected_hash:
                raise RuntimeError(f"Hash mismatch in archive file {rel_path}: expected {expected_hash}, got {actual_hash}")

        # Verify SHA256SUMS
        sums_path = extract_root / "SHA256SUMS"
        if not sums_path.exists():
            raise RuntimeError("Missing SHA256SUMS in extracted archive")

        for line in sums_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            expected_h, rel_f = parts
            target_f = extract_root / rel_f
            if not target_f.exists():
                raise RuntimeError(f"File listed in SHA256SUMS does not exist: {rel_f}")
            actual_h = sha256_file(target_f)
            if actual_h != expected_h:
                raise RuntimeError(f"SHA256SUMS hash mismatch for {rel_f}: expected {expected_h}, got {actual_h}")


# ---------------------------------------------------------------------------
# High-Level Bundle Command API
# ---------------------------------------------------------------------------

def bundle(
    skill_id: Optional[str] = None,
    profile_id: Optional[str] = None,
    adapter: str = "canonical",
    output_dir: Optional[Path] = None,
    selected_optionals: Optional[Set[str]] = None,
    all_optional: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Executes the bundle pipeline: stages, validates, packages, and verifies.
    """
    if not skill_id and not profile_id:
        raise ValueError("Must specify either skill_id or profile_id")
    if skill_id and profile_id:
        raise ValueError("Cannot specify both skill_id and profile_id")

    if output_dir is None:
        output_dir = ROOT / "dist"
    output_dir = Path(output_dir)

    normalized_adapter = "canonical"
    if adapter.lower() != "canonical":
        spec = normalize_adapter(adapter)
        normalized_adapter = spec.name

    with tempfile.TemporaryDirectory() as td:
        staging_root = Path(td)
        stage_dir, manifest, plan = stage_bundle(
            staging_root=staging_root,
            profile_id=profile_id,
            skill_id=skill_id,
            adapter=normalized_adapter,
            selected_optionals=selected_optionals,
            all_optional=all_optional,
        )

        pkg_name = manifest["package"]["name"]
        pkg_version = manifest["package"]["version"]
        archive_name = f"{pkg_name}-{pkg_version}-{normalized_adapter}.zip"
        output_zip = output_dir / archive_name
        output_sha256 = output_dir / f"{archive_name}.sha256"

        if dry_run:
            return {
                "status": "PLAN_ONLY",
                "archive_name": archive_name,
                "target_assistant": normalized_adapter,
                "package": manifest["package"],
                "build_mode": manifest["build_mode"],
                "git_commit": manifest["git_commit"],
                "artifacts": manifest["artifacts"],
                "warnings": manifest["warnings"],
                "file_count": len(manifest["file_hashes"]),
            }

        if output_zip.exists() and not force:
            raise FileExistsError(
                f"Archive already exists at '{output_zip}'. Use --force to overwrite."
            )

        # Build deterministic ZIP
        zip_sha256 = create_deterministic_zip(stage_dir, output_zip)

        # Write standalone companion sha256 checksum file
        output_sha256.write_text(f"{zip_sha256}  {archive_name}\n", encoding="utf-8")

        # Independent extraction verification
        verify_zip_archive(output_zip)

        return {
            "status": "SUCCESS",
            "archive_path": str(output_zip),
            "checksum_path": str(output_sha256),
            "archive_sha256": zip_sha256,
            "manifest": manifest,
        }


# ---------------------------------------------------------------------------
# CLI Command Handlers
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Agent Toolkit Deterministic ZIP Packaging Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # plan
    plan_parser = subparsers.add_parser("plan", help="Preview bundle manifest and artifacts without packaging")
    _add_target_args(plan_parser)
    plan_parser.add_argument("--json", action="store_true", help="Output plan as JSON")

    # build
    build_parser = subparsers.add_parser("build", help="Build deterministic, reproducible ZIP package")
    _add_target_args(build_parser)
    build_parser.add_argument(
        "--output-dir",
        default="dist",
        help="Target directory for generated ZIP archive and checksums (default: dist/)",
    )
    build_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing archive in output-dir if present",
    )
    build_parser.add_argument("--json", action="store_true", help="Output result as JSON")

    return parser


def _add_target_args(p: argparse.ArgumentParser) -> None:
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--profile", help="Name of profile to package (e.g. ui-ux, security-audit)")
    group.add_argument("--skill", help="ID of standalone skill to package (e.g. code-review, teach)")

    valid_adapter_choices = ["canonical"] + sorted(
        list(ADAPTER_SPECS.keys()) + [a for spec in ADAPTER_SPECS.values() for a in spec.aliases]
    )
    p.add_argument(
        "--agent",
        "--adapter",
        dest="agent",
        default="canonical",
        choices=valid_adapter_choices,
        help="Target assistant adapter (canonical, claude-code, codex, cursor, gemini-cli, github-copilot, opencode, antigravity). Default: canonical",
    )
    p.add_argument(
        "--with-optional",
        dest="with_optional",
        help="Comma-separated optional dependencies to include",
    )
    p.add_argument(
        "--all-optional",
        dest="all_optional",
        action="store_true",
        help="Include all optional dependencies",
    )


def cmd_plan(args: argparse.Namespace) -> int:
    optionals: Optional[Set[str]] = None
    if args.with_optional:
        optionals = {opt.strip() for opt in args.with_optional.split(",") if opt.strip()}

    try:
        res = bundle(
            skill_id=args.skill,
            profile_id=args.profile,
            adapter=args.agent,
            selected_optionals=optionals,
            all_optional=args.all_optional,
            dry_run=True,
        )
    except Exception as exc:
        print(f"Plan error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"Package: {res['package']['name']} v{res['package']['version']} ({res['package']['type']})")
        print(f"Target Assistant: {res['target_assistant']}")
        print(f"Build Mode: {res['build_mode']} (Git: {res['git_commit'][:8] if res['git_commit'] != 'unknown' else 'unknown'})")
        print(f"Archive Filename: {res['archive_name']}")
        print(f"Payload Files: {res['file_count']}")
        print("Artifacts:")
        for art in res["artifacts"]:
            print(f"  - [{art['group']}] {art['id']} ({art['canonical_path']})")
        if res["warnings"]:
            print("Warnings:")
            for w in res["warnings"]:
                print(f"  ! {w}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    optionals: Optional[Set[str]] = None
    if args.with_optional:
        optionals = {opt.strip() for opt in args.with_optional.split(",") if opt.strip()}

    try:
        res = bundle(
            skill_id=args.skill,
            profile_id=args.profile,
            adapter=args.agent,
            output_dir=Path(args.output_dir),
            selected_optionals=optionals,
            all_optional=args.all_optional,
            force=args.force,
            dry_run=False,
        )
    except Exception as exc:
        print(f"Build error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"Successfully packaged {res['manifest']['package']['name']} v{res['manifest']['package']['version']}")
        print(f"  Archive:  {res['archive_path']}")
        print(f"  Checksum: {res['checksum_path']}")
        print(f"  SHA-256:  {res['archive_sha256']}")
        print(f"  Build Mode: {res['manifest']['build_mode']}")
        if res["manifest"]["warnings"]:
            print("Notices:")
            for w in res["manifest"]["warnings"]:
                print(f"  ! {w}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.subcommand == "plan":
        return cmd_plan(args)
    elif args.subcommand == "build":
        return cmd_build(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
