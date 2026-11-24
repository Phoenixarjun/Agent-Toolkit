import json
import os
import re
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ['data/demo.js', 'data/workspace.js', 'scripts/components.js', 'scripts/app.js']
HTML = (ROOT / 'index.html').read_text(encoding='utf-8')
HTML = HTML.replace('<link rel="stylesheet" href="style.css">', '<style>' + (ROOT / 'style.css').read_text(encoding='utf-8') + '</style>')
HTML = re.sub(r'<script defer src="[^"]+"></script>', '', HTML)
DEMO = json.loads((ROOT / 'data/demo.json').read_text(encoding='utf-8'))


def load(browser, width, height):
    page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
    errors = []
    requests = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('request', lambda request: requests.append(request.url))
    page.set_content(HTML)
    for path in ASSETS:
        page.add_script_tag(content=(ROOT / path).read_text(encoding='utf-8'))
    return page, errors, requests


def route(page, value):
    page.evaluate('(value) => { location.hash = value; }', value)
    page.wait_for_function('(value) => document.querySelector("#nav a[aria-current=page]")?.getAttribute("href") === "#" + value.split("/")[0]', arg=value)
    page.wait_for_timeout(40)
    assert page.locator('h1').count() == 1, value


def import_json(page, data):
    page.locator('#snapshot-file').set_input_files({'name': 'snapshot.json', 'mimeType': 'application/json', 'buffer': json.dumps(data).encode()})


def run():
    executable = os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
    with sync_playwright() as p:
        options = {'args': ['--no-sandbox']}
        if executable:
            options['executable_path'] = executable
        browser = p.chromium.launch(**options)
        page, errors, requests = load(browser, 1536, 960)
        assert 'Transition to AI Engineer' in page.locator('h1').inner_text()
        assert '33%' in page.locator('.metrics').first.inner_text()
        assert 'Illustrative sample data' in page.locator('#notice').inner_text()
        if os.environ.get('CAREER_SCREENSHOT_DIR'):
            directory = Path(os.environ['CAREER_SCREENSHOT_DIR'])
            directory.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=directory / 'career-web-overview.png', full_page=True)
        for name in ['roadmap', 'tasks', 'projects', 'presence', 'content', 'resumes', 'opportunities', 'companies', 'applications', 'interviews', 'offers', 'research', 'activity', 'youtube']:
            route(page, name)
            assert 'not found' not in page.locator('h1').inner_text().lower(), name
        route(page, 'content')
        page.get_by_role('searchbox', name='Search records').fill('Retrieval')
        assert page.locator('tbody tr').count() == 1
        page.get_by_role('searchbox', name='Search records').fill('')
        page.get_by_role('combobox', name='Filter by status').select_option('PUBLISHED')
        assert page.locator('tbody tr').count() == 1
        page.get_by_role('combobox', name='Filter by status').select_option('')
        if os.environ.get('CAREER_SCREENSHOT_DIR'):
            page.screenshot(path=directory / 'career-web-content.png', full_page=True)
        page.get_by_role('link', name='Retrieval evaluation: what to measure').click()
        page.get_by_role('heading', name='Retrieval evaluation: what to measure').wait_for()
        page.get_by_role('link', name='Retrieval evaluation dossier').click()
        page.get_by_role('heading', name='Retrieval evaluation dossier').wait_for()
        assert 'Retrieve -> Rerank' in page.locator('pre').inner_text()
        route(page, 'research/market')
        assert page.locator('.doc table').count() == 1
        if os.environ.get('CAREER_SCREENSHOT_DIR'):
            page.screenshot(path=directory / 'career-web-research.png', full_page=True)
        route(page, 'interviews/practice')
        assert page.locator('.quiz-feedback').first.inner_text() == ''
        page.get_by_role('radio', name='Increasing the timeout only').check()
        page.get_by_role('button', name='Check answer').click()
        assert '0 correct / 1 checked' in page.locator('.quiz > .small').inner_text()
        page.get_by_role('radio', name='A stable idempotency key with durable result storage').check()
        assert '0 correct / 0 checked' in page.locator('.quiz > .small').inner_text()
        page.get_by_role('button', name='Check answer').click()
        assert '1 correct / 1 checked' in page.locator('.quiz > .small').inner_text()
        page.get_by_role('textbox', name='Answer to question 2').fill('Measure retrieval quality and groundedness.')
        page.get_by_role('button', name='Show review criteria').click()
        assert 'Self-review criteria' in page.locator('.quiz-feedback').last.inner_text()
        page.get_by_role('button', name='Prepare responses to copy').click()
        assert 'Measure retrieval quality' in page.get_by_role('textbox', name='Practice responses to copy').input_value()
        if os.environ.get('CAREER_SCREENSHOT_DIR'):
            page.evaluate('window.scrollTo(0,0)')
            page.screenshot(path=directory / 'career-web-interview.png', full_page=True)
        page.get_by_role('button', name='Reset practice').click()
        assert '0 correct / 0 checked' in page.locator('.quiz > .small').inner_text()
        assert not page.get_by_role('radio', name='A stable idempotency key with durable result storage').is_checked()
        route(page, 'overview')
        assert 'DUE' in page.get_by_role('row', name=re.compile('LinkedIn technical content')).inner_text()
        route(page, 'research/missing')
        assert page.locator('h1').inner_text() == 'Record not found'
        invalid = {'schema_version': 2}
        import_json(page, invalid)
        page.get_by_text('Snapshot not loaded:', exact=False).wait_for()
        assert page.locator('#source-label').inner_text() == 'Sample workspace'
        actual = json.loads(json.dumps(DEMO))
        actual['mode'] = 'workspace'
        actual['candidate']['target'] = 'Example target'
        actual['documents'][0]['markdown'] = '<img src=x onerror=globalThis.hacked=1>\n<script>globalThis.hacked=1</script>'
        import_json(page, actual)
        page.get_by_role('heading', name='Transition to Example target').wait_for()
        route(page, 'research/market')
        assert page.locator('.doc img').count() == 0
        assert '<script>' in page.locator('article.doc').inner_text()
        assert page.evaluate('globalThis.hacked') is None
        stage = json.loads(json.dumps(actual))
        stage['as_of'] = '2027-05-01'
        for m in stage['plan']['milestones']:
            if m['id'] not in ('interview','search'):
                stage['progress'][m['id']] = {'status':'COMPLETED','completed_at':stage['as_of'],'evidence_refs':['test-completion']}
        stage['plan']['milestones'][-1]['activation'] = 'CONDITIONAL'
        stage['plan']['milestones'][-1]['trigger'] = 'Candidate authorizes active search'
        stage['routines'][0]['next_due'] = '2027-05-07'
        stage['routines'][0]['summary'] = 'Prior weekly occurrence accepted; next not yet due.'
        stage['sections']['content'][0]['status'] = 'PUBLISHED'
        stage['sections']['content'][0]['fields'][1]['value'] = '2027-04-29'
        import_json(page, stage)
        page.get_by_role('heading', name='Transition to Example target').wait_for()
        assert 'interview' in page.locator('.task-row').first.inner_text().lower()
        assert 'search' not in page.locator('.task-row').first.inner_text().lower()
        assert 'ACTIVE' in page.get_by_role('row', name=re.compile('LinkedIn technical content')).inner_text()
        stage['progress']['search'].update({'activation_confirmed_at':'2027-05-01','activation_evidence_refs':['test-user-confirmed']})
        import_json(page, stage)
        page.get_by_text('Ready milestones', exact=True).wait_for()
        page.wait_for_function("document.querySelectorAll('.task-row').length === 2")
        stage['plan']['plan_id'] = 'v2-test'
        import_json(page, stage)
        page.get_by_text('HISTORICAL', exact=True).wait_for()
        route(page, 'content')
        assert '2027-04-29' in page.locator('tbody').inner_text()
        pending = {**stage, 'plan_state': 'PROPOSED'}
        import_json(page, pending)
        page.get_by_text('Proposed plan: v2-test', exact=True).wait_for()
        assert page.locator('.task-row').count() == 0
        direct = {**actual, 'plan': None, 'plan_state': 'UNKNOWN', 'progress': {}, 'routines': [], 'next_review': None}
        import_json(page, direct)
        page.get_by_text('No pillars recorded.').wait_for()
        for section in ['presence', 'projects', 'resumes', 'interviews']:
            route(page, section)
            assert page.locator('tbody tr').count() == len(direct['sections'][section]), section
        empty = {**actual, 'plan': None, 'plan_state': 'UNKNOWN', 'progress': {}, 'sections': {}, 'documents': [], 'activity': [], 'extensions': [], 'routines': [], 'next_review': None}
        import_json(page, empty)
        page.get_by_text('No pillars recorded.').wait_for()
        assert page.locator('#source-label').inner_text() == 'Workspace snapshot'
        page.get_by_role('button', name='Return to default').click()
        page.get_by_role('heading', name='Transition to AI Engineer').wait_for()
        assert not errors, errors
        assert not requests, requests
        mobile, mobile_errors, mobile_requests = load(browser, 390, 844)
        for name in ['overview', 'roadmap', 'content', 'research/market', 'youtube', 'interviews/practice']:
            route(mobile, name)
            assert mobile.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'), name
        assert not mobile_errors, mobile_errors
        assert not mobile_requests, mobile_requests
        browser.close()
    print('PASS: desktop and mobile in-memory Chromium rendering; 15 page routes, record/document navigation, search/filter, extension, missing records, invalid/valid/empty import, reset, literal untrusted content, recurring cadence, due and conditional milestones, plan revision, direct-mode records without a plan, objective and written quiz interactions, no page errors or network requests.')
    print('Direct file:// navigation is a separate manual target-browser smoke check.')


if __name__ == '__main__':
    run()
