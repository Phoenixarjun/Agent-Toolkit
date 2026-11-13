# Agent Toolkit - Deterministic ZIP Packaging Guide

This guide describes the architecture, operation, and security properties of Agent Toolkit's deterministic packaging engine (`scripts/bundle.py`).

The packaging system compiles canonical skills and composed capability profiles into byte-for-byte reproducible ZIP archives accompanied by cryptographic manifests and standalone SHA-256 checksums. It provides the distribution foundation for website downloads, offline archives, and downstream package managers without introducing external dependencies.

---

## 1. Architectural Principles

The packaging engine adheres strictly to Agent Toolkit's repository architecture:

1. **Single Source of Truth**: Artifacts originate from canonical locations (`skills/`, `workflows/`, `agents/`, `rules/`, `knowledge/`, `catalog/`, `profiles/`, `adapters/`).
2. **Zero Duplication**: `scripts/bundle.py` imports and reuses dependency resolution, catalog parsing, conflict detection, and runtime staging from `scripts/install.py` rather than implementing parallel logic.
3. **Deterministic Reproducibility**: Packaging the same Git commit and repository state on any platform produces byte-for-byte identical ZIP archives with matching SHA-256 digests.
4. **Safe Staging**: Packaging operations occur entirely inside isolated temporary directories, verifying payload integrity via `run_doctor` before archive creation.
5. **Non-Self-Referential Manifests**: Manifests compute cryptographic digests for all packaged files while strictly omitting the manifest itself, preventing circular hash dependencies.

---

## 2. Deterministic Archive Specification

To guarantee byte-for-byte reproducibility across operating systems, filesystems, and Python runtimes, `scripts/bundle.py` enforces the following constraints:

- **Fixed Epoch Timestamp**: All archive entries are assigned a constant datetime `2026-01-01 00:00:00 UTC` (`ZipInfo.date_time = (2026, 1, 1, 0, 0, 0)`).
- **Normalized File Permissions**:
  - Regular files: `0644` (`(0o644 | stat.S_IFREG) << 16`)
  - Directories: `0755` (`(0o755 | stat.S_IFDIR) << 16`)
- **Canonical Path Sorting**: Directory entries and file entries are discovered, normalized with POSIX forward slashes (`/`), and sorted strictly alphabetically before writing.
- **Path Sanitization**: Reject any entry containing parent directory references (`..`), leading slashes (`/`, `\\`), or Windows drive prefixes (`^[a-zA-Z]:`).
- **Standard Deflate Compression**: Utilizes standard `zipfile.ZIP_DEFLATED`.
- **Atomic File Writing**: Archives are written to a temporary `.zip.tmp` file and atomically moved to `<archive_name>.zip` upon complete, verified generation.

---

## 3. Package Layout & Metadata

Each generated ZIP package contains a self-verifying, self-documenting structure:

```text
<archive_root>/
├── bundle-manifest.json   # Cryptographic manifest, metadata, and dependency closure
├── SHA256SUMS             # Plaintext SHA-256 checksums for all archive files
├── INSTALL.md             # Inspection guide, safe extraction steps, and assurance notices
└── payload/               # Target assistant files or canonical .agent-toolkit/ resources
    ├── .agent-toolkit/
    │   ├── manifest.json  # Runtime tracking manifest
    │   └── ...
    └── [assistant-specific entrypoints & discovery directories]
```

### Manifest Schema (`bundle-manifest.json` v1.0.0)

| Field | Type | Description |
| :--- | :--- | :--- |
| `schema_version` | `string` | Version of the packaging schema (`"1.0.0"`). |
| `package` | `object` | Identity containing `name`, `version`, and `type` (`"skill"` or `"profile"`). |
| `build_mode` | `string` | `"release"` if Git working tree is completely clean; `"development"` if uncommitted or untracked changes exist. |
| `git_commit` | `string` | Full Git HEAD commit hash, or `"unknown"`. |
| `target_assistant` | `string` | Target adapter (`"canonical"`, `"claude-code"`, `"cursor"`, etc.). |
| `artifacts` | `array` | Complete list of resolved artifacts (`group`, `id`, `version`, `canonical_path`). |
| `required_dependencies` | `array` | IDs of all required dependency artifacts. |
| `optional_dependencies_included` | `array` | IDs of optional dependencies explicitly included. |
| `optional_dependencies_available` | `array` | IDs of optional dependencies known in catalog but skipped. |
| `verification_status` | `string` | `"verified"` following successful internal `run_doctor` validation. |
| `warnings` | `array` | Security assurance notices and trust boundary warnings. |
| `file_hashes` | `object` | Relative POSIX paths to SHA-256 hashes for all payload files and `INSTALL.md` (excludes `bundle-manifest.json`). |

---

## 4. CLI Usage

### A. Preview Packaging (`plan`)

Preview dependency closures, file counts, and warnings without generating files:

```bash
# Preview standalone skill package
python scripts/bundle.py plan --skill code-review

# Preview composed profile for a specific assistant
python scripts/bundle.py plan --profile ui-ux --adapter claude-code

# Preview with all optional dependencies included
python scripts/bundle.py plan --skill teach --all-optional

# Output preview as machine-readable JSON
python scripts/bundle.py plan --profile security-audit --json
```

### B. Build Package (`build`)

Stage, validate, build deterministic archive, and emit companion `.sha256` checksum:

```bash
# Package a standalone skill for canonical distribution
python scripts/bundle.py build --skill code-review --output-dir dist/

# Package a composed profile for Cursor
python scripts/bundle.py build --profile ui-ux --adapter cursor --output-dir dist/

# Package with selected optional dependencies
python scripts/bundle.py build --skill teach --with-optional research --output-dir dist/

# Force overwrite existing archive in output directory
python scripts/bundle.py build --skill security-audit --force --output-dir dist/
```

### Supported Target Assistants

Pass via `--adapter` or `--agent`:
- `canonical` (Default: pure shared resources under `.agent-toolkit/` without vendor files)
- `claude-code` (`claude`)
- `codex` (`openai-codex`)
- `cursor`
- `gemini-cli` (`gemini`)
- `github-copilot` (`copilot`)
- `opencode`
- `antigravity` (`agy`)

---

## 5. Security & Trust Boundaries

1. **Extraction Integrity**: Every build automatically performs an immediate extraction check in an isolated temporary directory, confirming that:
   - Archive passes internal ZIP CRC tests (`testzip()`).
   - Every entry path is sanitized against directory traversal attacks.
   - Every file matches its cryptographic digest in both `bundle-manifest.json` and `SHA256SUMS`.
2. **Safe Consumption**: `INSTALL.md` instructs consumers to inspect archives and warns against blind overwrites.
3. **Execution Assurance Boundary**: When packaging multi-agent workflows (such as `security-audit`), the package manifest and installation guide explicitly document that multi-agent security assurance requires isolated execution environments and that workflows statically bind to trusted `.agent-toolkit/workflows/` paths.
