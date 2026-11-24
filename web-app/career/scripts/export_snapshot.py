import argparse
import json
import os
import tempfile
import shutil
import subprocess
from pathlib import Path

MAX_BYTES = 20 * 1024 * 1024


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f'Invalid JSON number: {value}')


def private_path(path):
    path = Path(os.path.abspath(Path(path).expanduser()))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f'Symlink path is not supported: {part}')
        if (part / '.git').exists() or ((part / 'skills').is_dir() and (part / 'catalog').is_dir() and (part / 'agents').is_dir()):
            raise ValueError('Export only into a private workspace outside source repositories and Agent Toolkit')
    return path


def export(source, viewer):
    source, viewer = private_path(source), private_path(viewer)
    if not source.is_file() or source.stat().st_size > MAX_BYTES:
        raise ValueError('Source must be a JSON file no larger than 20 MB')
    if not (viewer / 'index.html').is_file() or not (viewer / 'scripts/components.js').is_file():
        raise ValueError('Choose a private copy of the Career viewer')
    target = private_path(viewer / 'data/workspace.js')
    if not target.parent.is_dir() or not target.is_file():
        raise ValueError('Viewer data/workspace.js is missing')
    payload = json.loads(source.read_text(encoding='utf-8'), object_pairs_hook=unique, parse_constant=invalid_constant)
    if not isinstance(payload, dict) or type(payload.get('schema_version')) is not int or payload['schema_version'] != 1 or payload.get('mode') != 'workspace':
        raise ValueError('Expected Career snapshot v1 with mode workspace; demo must remain demo')
    serialized = json.dumps(payload, ensure_ascii=True, allow_nan=False, separators=(',', ':'))
    node = shutil.which('node')
    if not node:
        raise ValueError('Node 18+ is required for optional persistent export validation; use the browser JSON picker instead')
    validator = Path(__file__).resolve().parent / 'components.js'
    code = 'require(process.argv[1]); const data=JSON.parse(require("node:fs").readFileSync(0,"utf8")); const errors=globalThis.CareerUI.validate(data); if(errors.length){console.error(errors.join("; "));process.exitCode=1;}'
    try:
        result = subprocess.run([node, '-e', code, str(validator)], input=serialized, text=True, capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError('Snapshot validation did not complete; previous export preserved') from exc
    if result.returncode:
        raise ValueError('Snapshot failed display validation: ' + result.stderr.strip()[:2000])
    script = 'globalThis.CAREER_WORKSPACE = JSON.parse(' + json.dumps(serialized, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026') + ');\n'
    fd, temp = tempfile.mkstemp(prefix='.snapshot-', suffix='.tmp', dir=target.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(script)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, target)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    return target


def main():
    parser = argparse.ArgumentParser(description='Serialize an approved Career JSON snapshot into a private copy of the offline viewer.')
    parser.add_argument('snapshot')
    parser.add_argument('viewer')
    args = parser.parse_args()
    try:
        result = export(args.snapshot, args.viewer)
    except (OSError, ValueError, RecursionError) as exc:
        parser.exit(1, f'Export failed: {exc}\n')
    print(f'Wrote {result}. Display contract validated before replacement; no canonical career records changed.')


if __name__ == '__main__':
    main()
