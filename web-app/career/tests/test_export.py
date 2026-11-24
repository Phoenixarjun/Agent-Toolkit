import importlib.util
import json
import subprocess
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('export_snapshot', ROOT / 'scripts/export_snapshot.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.viewer = self.root / 'viewer'
        shutil.copytree(ROOT, self.viewer, ignore=shutil.ignore_patterns('__pycache__'))
        self.source = self.root / 'snapshot.json'
        self.data = json.loads((ROOT / 'data/demo.json').read_text())
        self.data['mode'] = 'workspace'
        self.target = self.viewer / 'data/workspace.js'
        self.source.write_text(json.dumps(self.data))

    def tearDown(self):
        self.tmp.cleanup()

    def test_only_display_file_changed(self):
        before = {p.relative_to(self.viewer): p.read_bytes() for p in self.viewer.rglob('*') if p.is_file()}
        self.assertEqual(MODULE.export(self.source, self.viewer), self.target)
        after = {p.relative_to(self.viewer): p.read_bytes() for p in self.viewer.rglob('*') if p.is_file()}
        self.assertEqual([k.as_posix() for k in before if before[k] != after[k]], ['data/workspace.js'])

    def test_approved_plan_projection_and_revision(self):
        spec = importlib.util.spec_from_file_location('plan_store', ROOT.parents[1] / 'scripts/career/plan_store.py')
        store = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(store)
        plan = self.data['plan']
        plan['parent_plan_id'] = None
        def approve(p):
            return {'plan_id':p['plan_id'], 'plan_sha256':store.digest(p), 'decision':'APPROVE', 'approved_at':'2026-11-24T10:00:00+05:30','approval_reference':'Synthetic integration test'}
        store.stage(self.root, plan)
        self.assertIsNone(store.pointer(self.root))
        store.activate(self.root, plan['plan_id'], approve(plan))
        old = json.loads(json.dumps(plan))
        proposal = json.loads(json.dumps(plan))
        proposal.update(plan_id='v2-proposed', parent_plan_id=plan['plan_id'], review_rationale='Synthetic revision')
        store.stage(self.root, proposal)
        self.assertEqual(store.pointer(self.root)['plan_id'], old['plan_id'])
        self.source.write_text(json.dumps(self.data))
        MODULE.export(self.source, self.viewer)
        old_export = self.target.read_bytes()
        store.activate(self.root, proposal['plan_id'], approve(proposal))
        self.data['plan'] = store.read_json(self.root / 'strategy/plans/v2-proposed.json')
        self.source.write_text(json.dumps(self.data))
        before = {p:p.read_bytes() for p in (self.root / 'strategy').rglob('*.json')}
        MODULE.export(self.source, self.viewer)
        self.assertNotEqual(self.target.read_bytes(), old_export)
        self.assertEqual(before, {p:p.read_bytes() for p in before})
        self.assertEqual(store.read_json(self.root / 'strategy/plans' / (old['plan_id'] + '.json')), old)
        self.assertEqual(store.pointer(self.root)['plan_id'], proposal['plan_id'])

    def test_duplicate_keys_rejected(self):
        old = self.target.read_bytes()
        self.source.write_text('{"schema_version":1,"schema_version":2,"mode":"workspace"}')
        with self.assertRaises(ValueError):
            MODULE.export(self.source, self.viewer)
        self.assertEqual(self.target.read_bytes(), old)

    def test_invalid_body_preserves_previous_export(self):
        MODULE.export(self.source, self.viewer)
        old = self.target.read_bytes()
        self.data['sections']['interviews'][0]['blocks'][0]['questions'][0]['correct_index'] = 99
        self.source.write_text(json.dumps(self.data))
        with self.assertRaises(ValueError):
            MODULE.export(self.source, self.viewer)
        self.assertEqual(self.target.read_bytes(), old)

    def test_missing_validator_runtime_preserves_previous_export(self):
        from unittest.mock import patch
        old = self.target.read_bytes()
        with patch.object(MODULE.shutil, 'which', return_value=None):
            with self.assertRaises(ValueError):
                MODULE.export(self.source, self.viewer)
        self.assertEqual(self.target.read_bytes(), old)

    def test_demo_not_promoted(self):
        self.data['mode'] = 'demo'
        self.source.write_text(json.dumps(self.data))
        with self.assertRaises(ValueError):
            MODULE.export(self.source, self.viewer)

    def test_repository_refused(self):
        (self.root / '.git').mkdir()
        with self.assertRaises(ValueError):
            MODULE.export(self.source, self.viewer)

    def test_symlink_target_refused(self):
        self.target.unlink()
        try:
            self.target.symlink_to(self.source)
        except OSError:
            self.skipTest("Symlinks unavailable")
        with self.assertRaises(ValueError):
            MODULE.export(self.source, self.viewer)

    def test_nonfinite_rejected(self):
        self.data['extra'] = float('nan')
        self.source.write_text(json.dumps(self.data))
        with self.assertRaises(ValueError):
            MODULE.export(self.source, self.viewer)

    @unittest.skipUnless(shutil.which('node'), 'Node unavailable')
    def test_script_safe_round_trip(self):
        self.data['documents'][0]['markdown'] = '</script>\n<script>globalThis.hacked=1</script>\n"\\\u2028'
        self.source.write_text(json.dumps(self.data))
        MODULE.export(self.source, self.viewer)
        result = subprocess.check_output(['node', '-e', 'require(process.argv[1]); console.log(JSON.stringify([globalThis.CAREER_WORKSPACE,globalThis.hacked||null]))', str(self.target)], text=True)
        payload, injected = json.loads(result)
        self.assertEqual(payload, self.data)
        self.assertIsNone(injected)
        self.assertNotIn('</script>', self.target.read_text())


if __name__ == '__main__':
    unittest.main()
