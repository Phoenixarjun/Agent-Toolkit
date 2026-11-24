#!/usr/bin/env python3
"""
scripts/compile_distribution.py

Compiles canonical Agent Toolkit catalog, capability definitions, and installation
plans into validated, machine-readable distribution resources and contracts for the
pure Node.js npm CLI package.

Reuses the authoritative Python dependency resolver and installation planner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import install


def get_git_commit() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "unknown"


def sha256_content(content: str | bytes) -> str:
    hasher = hashlib.sha256()
    if isinstance(content, str):
        hasher.update(content.encode("utf-8"))
    else:
        hasher.update(content)
    return hasher.hexdigest()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compile_distribution(output_dir: Path, version: str = "0.1.0") -> Dict[str, Any]:
    print(f"Compiling distribution into {output_dir.as_posix()}...")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    resources_dir = output_dir / "resources"
    contracts_dir = resources_dir / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)

    git_commit = get_git_commit()
    catalog = install.get_catalog()
    profiles = install.get_profiles()

    # Collect installable skills and profiles
    skills_meta = []
    for sk in catalog.get("skills", []):
        sk_id = sk["id"]
        skills_meta.append({
            "id": sk_id,
            "version": sk.get("version", "1.0.0"),
            "category": sk.get("category", "engineering"),
            "domains": sk.get("domains", []),
            "maturity": sk.get("maturity", "stable"),
            "optional_dependencies": sk.get("optional_dependencies", {}),
            "dependencies": sk.get("dependencies", {}),
            "has_optional": bool(sk.get("optional_dependencies")),
        })

    profiles_meta = []
    for p_id, p_data in profiles.items():
        profiles_meta.append({
            "id": p_id,
            "name": p_data.get("name", p_id),
            "description": p_data.get("description", ""),
            "skills": p_data.get("skills", []),
            "workflows": p_data.get("workflows", []),
            "agents": p_data.get("agents", []),
            "rules": p_data.get("rules", []),
            "knowledge": p_data.get("knowledge", []),
        })

    adapters_meta = []
    for spec_name, spec in install.ADAPTER_SPECS.items():
        adapters_meta.append({
            "name": spec.name,
            "aliases": spec.aliases,
            "preferred_skill_root": spec.preferred_skill_root,
            "secondary_skill_roots": spec.secondary_skill_roots,
            "entrypoint_file": spec.entrypoint_file,
            "agent_root": spec.agent_root,
            "display_name": spec.display_name,
            "description": spec.description,
            "supports_specialist_agents": spec.supports_specialist_agents,
        })

    # Compile contracts for all skills and profiles across all adapters
    contracts_index: Dict[str, str] = {}
    copied_sources: Set[str] = set()

    dummy_target = Path("/tmp/dummy_project") if os.name != "nt" else Path("C:/dummy_project")

    # List of combinations: (type, id, has_optional)
    targets_to_compile = []
    for sk in skills_meta:
        targets_to_compile.append(("skill", sk["id"], sk["has_optional"]))
    for pr in profiles_meta:
        # Check if profile skills have optionals
        has_opt = any(
            bool(catalog.get("skills", {}) and next((s.get("optional_dependencies") for s in catalog.get("skills", []) if s["id"] == s_id), None))
            for s_id in pr["skills"]
        )
        targets_to_compile.append(("profile", pr["id"], has_opt))

    total_compiled = 0
    for target_type, target_id, has_opt in targets_to_compile:
        modes = [False]
        if has_opt:
            modes.append(True)

        for all_opt in modes:
            for adapter_name in install.ADAPTER_SPECS.keys():
                spec = install.ADAPTER_SPECS[adapter_name]
                
                # Build canonical installation plan
                if target_type == "skill":
                    plan = install.build_installation_plan(
                        dummy_target,
                        adapter=adapter_name,
                        skill_id=target_id,
                        all_optional=all_opt,
                    )
                    cap_version = next((s["version"] for s in skills_meta if s["id"] == target_id), "1.0.0")
                else:
                    plan = install.build_installation_plan(
                        dummy_target,
                        adapter=adapter_name,
                        profile_id=target_id,
                        all_optional=all_opt,
                    )
                    cap_version = "1.0.0"

                # Extract file operations
                contract_files = []
                for pf in plan.files:
                    f_info = {
                        "rel_destination": pf.rel_destination,
                        "source_path": pf.source_path,
                        "is_adapter_specific": pf.is_adapter_specific,
                    }
                    if pf.content is not None:
                        f_info["content"] = pf.content
                        f_info["sha256"] = sha256_content(pf.content)
                    elif pf.source_path:
                        src_full = ROOT / pf.source_path
                        if src_full.exists():
                            f_info["sha256"] = sha256_file(src_full)
                            copied_sources.add(pf.source_path)
                        else:
                            f_info["sha256"] = None
                    contract_files.append(f_info)

                # Generate managed entrypoint block
                managed_block = install.generate_managed_entrypoint(spec, dummy_target, plan.artifacts, plan.aliases)

                # Extract companion apps if any
                companion_apps = []
                for a in plan.artifacts:
                    if a.group == "apps":
                        app_name = a.id.replace("-viewer", "")
                        companion_apps.append({
                            "id": a.id,
                            "name": app_name,
                            "destination": f".agent-toolkit/apps/{app_name}",
                            "entrypoint": "index.html",
                        })

                # Runtime requirements
                runtime_requirements = []
                if any(a.id == "career" for a in plan.artifacts):
                    runtime_requirements.append({
                        "capability": "career",
                        "prerequisite": "python>=3.10",
                        "optional": True,
                        "description": "Optional local plan store and document serializer",
                    })

                contract_data = {
                    "schemaVersion": "1.0.0",
                    "capability": {
                        "id": target_id,
                        "type": target_type,
                        "version": cap_version,
                    },
                    "adapter": adapter_name,
                    "allOptional": all_opt,
                    "resolvedArtifacts": [
                        {
                            "group": a.group,
                            "id": a.id,
                            "version": a.version,
                            "canonicalPath": a.canonical_path,
                        }
                        for a in plan.artifacts
                    ],
                    "optionalIncluded": plan.optional_included,
                    "optionalSkipped": plan.optional_skipped,
                    "files": contract_files,
                    "entrypoint": {
                        "file": spec.entrypoint_file,
                        "managedBlock": managed_block,
                    },
                    "companionApps": companion_apps,
                    "runtimeRequirements": runtime_requirements,
                    "warnings": plan.warnings,
                }

                # Contract file path
                opt_suffix = "-all-optional" if all_opt else ""
                contract_rel = f"contracts/{target_type}s/{target_id}/{adapter_name}{opt_suffix}.json"
                contract_full = resources_dir / contract_rel
                contract_full.parent.mkdir(parents=True, exist_ok=True)
                with contract_full.open("w", encoding="utf-8") as h:
                    json.dump(contract_data, h, indent=2)

                index_key = f"{target_type}:{target_id}:{adapter_name}:{'all_opt' if all_opt else 'default'}"
                contracts_index[index_key] = contract_rel
                total_compiled += 1

    # Copy all referenced source files into resources/
    print(f"Copying {len(copied_sources)} unique referenced source files into resources/...")
    for src_rel in sorted(copied_sources):
        src_path = ROOT / src_rel
        if src_path.exists():
            dest_path = resources_dir / src_rel
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)

    # Compile distribution-index.json
    dist_index = {
        "packageName": "@agent-toolkit-core/cli",
        "packageVersion": version,
        "cliExecutable": "agent-toolkit",
        "schemaVersion": "1.0.0",
        "sourceCommit": git_commit,
        "skills": skills_meta,
        "profiles": profiles_meta,
        "adapters": adapters_meta,
        "companionApps": [
            {
                "id": "career-viewer",
                "name": "career",
                "path": "apps/career",
                "entrypoint": "index.html",
                "description": "Offline career workspace and document projection viewer",
            },
            {
                "id": "visualize-viewer",
                "name": "visualize",
                "path": "apps/visualize",
                "entrypoint": "index.html",
                "description": "Offline 2D/3D architecture explorer and simulation runner",
            },
        ],
        "contractsIndex": contracts_index,
    }

    index_path = resources_dir / "distribution-index.json"
    with index_path.open("w", encoding="utf-8") as h:
        json.dump(dist_index, h, indent=2)

    # Copy CLI source from packages/cli
    cli_src_dir = ROOT / "packages" / "cli"
    if cli_src_dir.exists():
        for d in ["bin", "src"]:
            src_sub = cli_src_dir / d
            if src_sub.exists():
                dest_sub = output_dir / d
                shutil.copytree(src_sub, dest_sub)

        for f in ["package.json", "README.md"]:
            src_f = cli_src_dir / f
            if src_f.exists():
                shutil.copy2(src_f, output_dir / f)

    # Copy LICENSE
    license_src = ROOT / "LICENSE"
    if license_src.exists():
        shutil.copy2(license_src, output_dir / "LICENSE")

    print(f"SUCCESS: Compiled {total_compiled} contracts into {output_dir.as_posix()}")
    return dist_index


def main():
    parser = argparse.ArgumentParser(description="Agent Toolkit Canonical Distribution Compiler")
    parser.add_argument("--output-dir", default="dist/npm/cli", help="Output staging directory")
    parser.add_argument("--version", default="0.1.0", help="Distribution package version")
    args = parser.parse_args()

    out_path = Path(args.output_dir)
    if not out_path.is_absolute():
        out_path = ROOT / out_path

    compile_distribution(out_path, version=args.version)


if __name__ == "__main__":
    main()
