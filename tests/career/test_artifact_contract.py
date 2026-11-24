import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / 'skills/career/SKILL.md'
AGENTS = {p.parent.name: p for p in (ROOT / 'agents/career').glob('*/AGENT.md')}
WORKFLOWS = {p.parent.name: p for p in (ROOT / 'workflows/career').glob('*/WORKFLOW.md')}
REFERENCES = {p.name for p in (ROOT / 'skills/career/references').glob('*.md')}


class ArtifactContractTests(unittest.TestCase):
    def test_single_entry(self):
        self.assertEqual([p for p in (ROOT / 'skills/career').rglob('SKILL.md')], [SKILL])

    def test_frontmatter_matches_path(self):
        for name, path in {**AGENTS, **WORKFLOWS, 'career': SKILL}.items():
            text = path.read_text(encoding='utf-8')
            self.assertTrue(text.startswith('---\n'), path)
            front = text.split('---\n', 2)[1]
            self.assertRegex(front, rf'(?m)^name: {re.escape(name)}$')
            self.assertRegex(front, r'(?m)^description: .+')

    def test_route_table_is_complete(self):
        routes = set(re.findall(r'\| (career-[a-z-]+) \|', SKILL.read_text(encoding='utf-8')))
        self.assertEqual(routes, set(WORKFLOWS))

    def test_profile_includes_all_roles_and_flows(self):
        profile = (ROOT / 'profiles/career.yaml').read_text(encoding='utf-8')
        for name in {*AGENTS, *WORKFLOWS, 'career-integrity'}:
            self.assertIn(f'- {name}\n', profile)

    def test_all_named_career_roles_resolve(self):
        for p in [SKILL, *WORKFLOWS.values(), *AGENTS.values()]:
            for ref in re.findall(r'`(career-[a-z-]+)`', p.read_text(encoding='utf-8')):
                self.assertIn(ref, {*AGENTS, *WORKFLOWS}, (p, ref))

    def test_references_resolve(self):
        for p in [SKILL, *WORKFLOWS.values(), *AGENTS.values()]:
            for ref in re.findall(r'`(?:references/)?([a-z-]+\.md)`', p.read_text(encoding='utf-8')):
                self.assertIn(ref, REFERENCES, (p, ref))

    def test_distinct_routes(self):
        text = SKILL.read_text(encoding='utf-8')
        self.assertRegex(text, r'\| linkedin;[^\n]+\| career-linkedin-profile \|')
        self.assertRegex(text, r'\| content \+ linkedin;[^\n]+\| career-linkedin-content \|')
        self.assertRegex(text, r'\| content \+ blog;[^\n]+\| career-blog \|')

    def test_entry_state_modes_and_audit_dispositions(self):
        skill_text = SKILL.read_text(encoding='utf-8')
        for mode in ('--plan', '--import-plan', '--audit-plan', '--continue', '--review'):
            self.assertIn(mode, skill_text)
        plan_wf = WORKFLOWS['career-plan'].read_text(encoding='utf-8')
        for disposition in ('KEEP', 'KEEP_WITH_OBSERVATIONS', 'REVISION_RECOMMENDED', 'INSUFFICIENT_EVIDENCE'):
            self.assertIn(disposition, plan_wf)
        delegation = (ROOT / 'skills/career/references/delegation-and-review.md').read_text(encoding='utf-8')
        for tier in ('DIRECT', 'FOCUSED', 'DEEP'):
            self.assertIn(tier, delegation)


if __name__ == '__main__':
    unittest.main()
