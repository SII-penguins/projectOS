"""Lifecycle consistency across combined documents, dependencies and archives."""
import json
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import test_projectos_tools as fixtures

AUDITOR, COMMON, TODAY = fixtures.AUDITOR, fixtures.COMMON, fixtures.TODAY


class LifecycleIntegrityTest(unittest.TestCase):
    write = fixtures.ProjectOSToolsTest.write
    make_base_project = fixtures.ProjectOSToolsTest.make_base_project
    run_command = fixtures.ProjectOSToolsTest.run_command
    audit_json = fixtures.ProjectOSToolsTest.audit_json

    def codes(self, root):
        return {f['code'] for f in self.audit_json(root)['findings']}

    def archive(self, root, row, path='doc/archive/TASKS.md'):
        self.write(root, path, COMMON.format(owner='terminal outcomes') +
                   '\n| ID | Status | Evidence | Outcome |\n| --- | --- | --- | --- |\n' + row + '\n')

    def test_combined_document_sections_do_not_leak_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, 'AGENTS.md', COMMON.format(owner='routing'))
            content = COMMON.format(owner='separate sections for current state and history') + '''
As Of: 2026-08-21
Plan Version: 1

## State
Current Phase: S1
Next Task: T-002
Next Action: Continue after T-001.

## Active work
| ID | Status | Owner | Dependencies | Next Action | Acceptance Gate | Evidence | Last Touched |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-002 | Ready | main | T-001 | Check | passes | pending | 2026-08-21 |

## Roadmap
| Stage | Status |
| --- | --- |
| S1 | Active |

## History
| ID | Status | Evidence | Outcome |
| --- | --- | --- | --- |
| T-001 | Done | check.log | accepted |
'''
            self.write(root, 'PROJECT.md', content)
            self.write(root, 'projectos.audit.json', json.dumps({'documents': {
                key: {'path': 'PROJECT.md', 'section': section}
                for key, section in [('progress', 'State'), ('todo', 'Active work'),
                                     ('plan', 'Roadmap'), ('archive', 'History')]
            }}))
            payload = self.audit_json(root)
            self.assertEqual(payload['findings'], [])
            self.assertEqual(payload['coverage']['active_task_rows'], 1)
            self.assertEqual(payload['coverage']['archive_task_rows'], 1)
            self.assertIn('next_action', payload['coverage']['checks'])
            p = root / 'PROJECT.md'
            p.write_text(content + '\n'.join('Historical observation' for _ in range(300)), encoding='utf-8')
            self.assertNotIn('PROGRESS_TOO_LARGE', self.codes(root))

    def test_missing_or_ambiguous_section_is_not_silently_scanned(self):
        for text, section in [('## Work\nhello\n', 'Absent'),
                              ('## Work\nfirst\n## Work\nsecond\n', 'Work')]:
            with self.subTest(text=text), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.write(root, 'PROJECT.md', text)
                self.write(root, 'projectos.audit.json', json.dumps({'documents': {
                    'todo': {'path': 'PROJECT.md', 'section': section}}}))
                result = self.run_command(str(AUDITOR), str(root))
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_combined_roles_share_one_source_revision(self):
        spec = importlib.util.spec_from_file_location('auditor_under_test', AUDITOR)
        auditor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(auditor)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'PROJECT.md'
            self.write(root, 'PROJECT.md', 'Revision: old\n\n## State\nold state\n\n## Work\nold work\n')
            original_read = Path.read_text

            def changing_read(path, *args, **kwargs):
                value = original_read(path, *args, **kwargs)
                if path == source:
                    path.write_text(value.replace('old', 'new'), encoding='utf-8')
                return value

            cfg = {'documents': {'progress': {'path': 'PROJECT.md', 'section': 'State'},
                                 'todo': {'path': 'PROJECT.md', 'section': 'Work'}}}
            with mock.patch.object(Path, 'read_text', changing_read):
                views = auditor.discover(root, cfg)
            self.assertIn('Revision: old', views['progress'][1])
            self.assertIn('Revision: old', views['todo'][1])
            self.assertIn('old work', views['todo'][1])

    def test_empty_audit_does_not_report_clean_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = self.audit_json(Path(tmp))
            self.assertTrue(any(f['code'] == 'NO_DOCUMENTS' for f in payload['findings']))
            self.assertEqual(payload['coverage']['documents'], [])
            self.assertEqual(payload['coverage']['checks'], [])

    def test_escaped_pipe_is_valid_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            p = root / 'TODO.md'
            p.write_text(p.read_text(encoding='utf-8').replace('Check passes', r'Output is a\|b'), encoding='utf-8')
            self.assertEqual(self.audit_json(root)['findings'], [])

    def test_unclosed_fence_cannot_hide_a_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            p = root / 'TODO.md'
            p.write_text('```markdown\n' + p.read_text(encoding='utf-8'), encoding='utf-8')
            self.assertIn('UNCLOSED_FENCE', self.codes(root))

    def test_explicit_next_task_overrides_historical_mention(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.archive(root, '| T-099 | Done | pass.log | accepted |')
            p = root / 'PROGRESS.md'
            p.write_text(p.read_text(encoding='utf-8').replace(
                'Next Action: Execute `T-001` after confirming its acceptance gate.',
                'Next Task: T-001\nNext Action: After T-099, execute T-001.'), encoding='utf-8')
            self.assertNotIn('NEXT_TASK_NOT_ACTIVE', self.codes(root))

    def test_multiple_next_references_require_interpretation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            p = root / 'PROGRESS.md'
            p.write_text(p.read_text(encoding='utf-8').replace(
                'Next Action: Execute `T-001` after confirming its acceptance gate.',
                'Next Action: After T-099, execute T-001.'), encoding='utf-8')
            codes = self.codes(root)
            self.assertIn('NEXT_TASK_AMBIGUOUS', codes)
            self.assertNotIn('NEXT_TASK_NOT_ACTIVE', codes)

    def test_dependencies_and_cycles_are_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(root, 'TODO.md', COMMON.format(owner='active tasks') + '''
| ID | Status | Dependencies |
| --- | --- | --- |
| T-001 | Ready | T-002 |
| T-002 | Blocked | T-001 |
| T-003 | Pending | T-404 |
''')
            codes = self.codes(root)
            self.assertIn('DEPENDENCY_CYCLE', codes)
            self.assertIn('DEPENDENCY_NOT_DONE', codes)
            self.assertIn('DEPENDENCY_UNKNOWN', codes)

    def test_cancelled_dependency_does_not_count_as_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.archive(root, '| T-099 | Cancelled | decision D1 | removed from scope |')
            p = root / 'TODO.md'
            p.write_text(p.read_text(encoding='utf-8').replace('| None |', '| T-099 |'), encoding='utf-8')
            self.assertIn('DEPENDENCY_NOT_DONE', self.codes(root))

    def test_duplicate_archived_ids_are_not_overwritten_by_last_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.archive(root, '| T-099 | Done | pass.log | accepted |')
            self.archive(root, '| T-099 | Cancelled | decision D1 | cancelled |', 'doc/archive/tasks/old.md')
            self.assertIn('ARCHIVE_ID_DUPLICATE', self.codes(root))

    def test_terminal_record_needs_nonplaceholder_outcome_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.archive(root, '| T-099 | Done | Pending | accepted |')
            self.assertIn('ARCHIVE_EVIDENCE_MISSING', self.codes(root))

    def test_retired_contract_cannot_masquerade_as_active_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(root, 'doc/PRD.md', COMMON.format(owner='goal and claims').replace('Status: Active', 'Status: Superseded') +
                       '\nContract Version: 1\nLast Verified Against: commit 123\n')
            self.assertIn('NONCURRENT_OWNER', self.codes(root))

    def test_fresh_document_date_does_not_refresh_old_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            p = root / 'TODO.md'
            p.write_text(p.read_text(encoding='utf-8').replace('| 2026-08-21 |', '| 2026-01-01 |'), encoding='utf-8')
            self.assertIn('TASK_STALE', self.codes(root))
            self.assertNotIn('TODO_STALE', self.codes(root))

    def test_empty_acceptance_and_future_task_date_need_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            p = root / 'TODO.md'
            p.write_text(p.read_text(encoding='utf-8').replace('| Check passes |', '|  |').replace(
                '| 2026-08-21 |', '| 2027-01-01 |'), encoding='utf-8')
            codes = self.codes(root)
            self.assertIn('TASK_FIELD_EMPTY', codes)
            self.assertIn('FUTURE_DATE', codes)


if __name__ == '__main__':
    unittest.main()
