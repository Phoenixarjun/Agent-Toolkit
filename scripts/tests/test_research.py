"""Offline negative/positive gates. This does not run live research agents."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCRIPTS=ROOT/'scripts'
sys.path.insert(0,str(SCRIPTS))
from validate_research import check_record
from render_research import render, TEMPLATE
FIXTURE=ROOT/'evals/research/fixtures/research-example.json'

class ResearchRecordTests(unittest.TestCase):
    def setUp(self):self.r=json.loads(FIXTURE.read_text())
    def assertInvalid(self,phrase):
        errors=check_record(self.r)
        self.assertTrue(any(phrase in error for error in errors),errors)
    def test_example_valid(self):self.assertEqual(check_record(self.r),[])
    def test_synthetic_is_never_complete(self):
        self.r['research']['outcome']='complete';self.assertInvalid('synthetic fixtures')
    def test_deep_complete_without_independent_contexts(self):
        self.r['research']['synthetic']=False;self.r['research']['outcome']='complete'
        for q in self.r['questions']:q['status']='answered'
        self.assertInvalid('deep complete requires actual independent')
    def test_reviewer_same_as_scout_rejected(self):
        c=self.r['claims'][0];c['scout_context']='ctx';c['verification']['reviewer_context']='ctx'
        self.assertInvalid('must differ from discoverer')
    def test_duplicate_agent_contexts_rejected(self):
        self.r['execution'].update(independence='independent',scout_contexts=['ctx'],critic_context='ctx')
        self.assertInvalid('role contexts must be unique')
    def test_answered_question_requires_claim(self):
        self.r['questions'][0].update(status='answered',claim_ids=[]);self.assertInvalid('answered requires supporting')
    def test_reciprocal_question_claim_link(self):
        self.r['questions'][0]['claim_ids']=['C-002'];self.assertInvalid('belongs to other question')
    def test_unknown_source(self):
        self.r['claims'][0]['source_ids']=['S-999'];self.assertInvalid('unknown source')
    def test_script_url_prohibited(self):
        self.r['sources'][0]['url']='javascript:alert(1)';self.assertInvalid('external URL must be HTTP')
    def test_embedded_credentials_prohibited(self):
        self.r['sources'][0]['url']='https://bob:secret@example.org/test';self.assertInvalid('without embedded credentials')
    def test_publication_later_than_access(self):
        self.r['sources'][0]['published_at']='2026-10-14';self.assertInvalid('publication cannot postdate access')
    def test_access_after_asof(self):
        self.r['sources'][0]['accessed_at']='2026-11-01';self.assertInvalid('access cannot postdate report')
    def test_chart_series_future_point(self):
        self.r['charts'][0]['series'][0]['points'][-1]['x']='2027-09-01';self.assertInvalid('future observation')
    def test_chart_duplicate_date(self):
        self.r['charts'][0]['series'][0]['points'][1]['x']='2026-07-01';self.assertInvalid('strictly increasing')
    def test_chart_nonfinite(self):
        self.r['charts'][0]['series'][0]['points'][0]['y']=float('nan');self.assertInvalid('finite numeric')
    def test_invalid_numeric_delta(self):
        self.r['claims'][0]['numeric_assertion']['delta']=9;self.assertInvalid('do not match chart observations')
    def test_claim_and_chart_source_mismatch(self):
        self.r['claims'][0]['source_ids']=['S-002'];self.assertInvalid('share at least one evidence source')
    def test_qualified_without_limitation(self):
        self.r['claims'][0]['limitations']=[];self.assertInvalid('uncertainty requires explicit limitation')
    def test_budget_overrun(self):
        self.r['execution']['budget']['scout_tasks_used']=15;self.assertInvalid('consumed <=')
    def test_validator_nonmutating(self):
        initial=copy.deepcopy(self.r);check_record(self.r);self.assertEqual(self.r,initial)
    def test_escapes_untrusted_content(self):
        self.r['research']['title']='<script>alert(1)</script>'
        self.r['sources'][0]['excerpt']='<img src=x onerror=alert(2)>'
        page=render(self.r,TEMPLATE.read_text())
        self.assertNotIn('<script>alert(1)</script>',page)
        self.assertNotIn('<img src=x onerror=alert(2)>',page)
        self.assertIn('&lt;script&gt;',page)
        self.assertIn('&lt;img',page)
    def test_markdown_uses_same_source_records(self):
        from render_research import render_markdown
        md=render_markdown(self.r)
        self.assertIn('C-001',md)
        self.assertIn('https://example.org/demo/deliveries',md)
        self.assertIn('88',md)
        self.assertIn('2026-09-01',md)
        self.assertIn('SYNTHETIC DEMO',md)
    def test_html_and_markdown_reflect_same_claim(self):
        from render_research import render_markdown
        statement=self.r['claims'][0]['text']
        self.assertIn(statement,render(self.r,TEMPLATE.read_text()))
        self.assertIn(statement,render_markdown(self.r))
    def test_renderer_blocks_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'bad.json';dest=Path(d)/'rendered.html'
            self.r['sources'][0]['url']='file:///private/data';f.write_text(json.dumps(self.r))
            res=subprocess.run([sys.executable,str(SCRIPTS/'render_research.py'),str(f),'--output',str(dest)],capture_output=True,text=True)
            self.assertNotEqual(res.returncode,0);self.assertFalse(dest.exists())
    def test_chart_has_accessible_table_and_source(self):
        page=render(self.r,TEMPLATE.read_text())
        self.assertIn('View source observations as a table',page)
        self.assertIn('href="#source-S-001"',page)
        self.assertIn('2026-09-01',page)
    def test_no_em_dash_in_report_template(self):
        self.assertNotIn('—',TEMPLATE.read_text())

if __name__=='__main__':unittest.main()
