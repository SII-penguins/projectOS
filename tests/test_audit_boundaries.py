"""Behavioral regressions for the auditor's advertised input/output contract."""
import json
from pathlib import Path
import tempfile
import unittest

import test_projectos_tools as fixtures

AUDITOR, COMMON, TODAY = fixtures.AUDITOR, fixtures.COMMON, fixtures.TODAY


class AuditBoundaryTest(unittest.TestCase):
    write = fixtures.ProjectOSToolsTest.write
    make_base_project = fixtures.ProjectOSToolsTest.make_base_project
    run_command = fixtures.ProjectOSToolsTest.run_command
    audit_json = fixtures.ProjectOSToolsTest.audit_json

    def codes(self, root):
        return {item['code'] for item in self.audit_json(root)['findings']}

    def test_documented_run_registry_mapping_is_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(root, 'records/RUNS.md', COMMON.format(owner='run history') +
                       '\n| ID | Outcome |\n| --- | --- |\n| R-1 | failed |\n')
            self.write(root, 'projectos.audit.json', json.dumps({
                'documents': {'run_registry': 'records/RUNS.md'}}))
            self.assertIn('RUN_TRUST_MISSING', self.codes(root))

    def test_explicit_missing_inputs_fail_instead_of_reporting_clean(self):
        for cfg, extra in [({'documents': {'todo': 'missing.md'}}, []),
                           ({}, ['--config', 'missing.json'])]:
            with self.subTest(cfg=cfg, extra=extra), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_base_project(root)
                self.write(root, 'projectos.audit.json', json.dumps(cfg))
                result = self.run_command(str(AUDITOR), str(root), *extra)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_output_cannot_overwrite_audited_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            target = root / 'TODO.md'
            before = target.read_bytes()
            result = self.run_command(str(AUDITOR), str(root), '--output', str(target))
            self.assertEqual(target.read_bytes(), before)
            self.assertEqual(result.returncode, 2)

    def test_external_report_preserves_project_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / 'project'
            self.make_base_project(root)
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            report = parent / 'report.json'
            result = self.run_command(str(AUDITOR), str(root), '--today', TODAY,
                                      '--format', 'json', '--output', str(report))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(report.read_text(encoding='utf-8'))['read_only'])
            self.assertEqual(before, {p.relative_to(root): p.read_bytes()
                                      for p in root.rglob('*') if p.is_file()})

    def test_external_hardlink_cannot_overwrite_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / 'project'
            self.make_base_project(root)
            target = root / 'TODO.md'
            report = parent / 'report.md'
            try:
                report.hardlink_to(target)
            except OSError as exc:
                self.skipTest(f'Hard links unavailable: {exc}')
            before = target.read_bytes()
            result = self.run_command(str(AUDITOR), str(root), '--output', str(report))
            self.assertEqual(result.returncode, 2)
            self.assertEqual(target.read_bytes(), before)

    def test_legacy_run_mapping_and_optional_null_are_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(root, 'records/RUNS.md', COMMON.format(owner='run history') +
                       '\n| ID | Trust |\n| --- | --- |\n')
            self.write(root, 'doc/PRD.md', 'Unused draft contract.\n')
            self.write(root, 'projectos.audit.json', json.dumps({
                'documents': {'run': 'records/RUNS.md', 'prd': None}}))
            self.assertEqual(self.audit_json(root)['findings'], [])

    def test_later_task_tables_are_audited(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(root, 'doc/archive/TASKS.md', COMMON.format(owner='terminal tasks') +
                       '\n| ID | Status |\n| --- | --- |\n| T-090 | Done |\n\n'
                       '## Another phase\n\n| ID | Status |\n| --- | --- |\n| T-091 | Blocked |\n')
            self.assertIn('ARCHIVE_ACTIVE_TASK', self.codes(root))
            todo = root / 'TODO.md'
            todo.write_text(todo.read_text(encoding='utf-8') +
                            '\n## Next phase\n\n| ID | Status |\n| --- | --- |\n| T-092 | Done |\n',
                            encoding='utf-8')
            self.assertIn('TERMINAL_TASK_ACTIVE', self.codes(root))

    def test_unknown_archive_status_is_not_certified_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(root, 'doc/archive/TASKS.md', COMMON.format(owner='terminal tasks') +
                       '\n| ID | Status |\n| --- | --- |\n| T-090 | awaiting evidence |\n')
            findings = self.audit_json(root)['findings']
            self.assertTrue(any(f['code'] == 'ARCHIVE_STATUS_UNKNOWN' and
                                f['severity'] == 'ERROR' for f in findings))

    def test_status_alias_cannot_make_blocked_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(root, 'projectos.audit.json', json.dumps({'terminal_task_statuses': ['Blocked']}))
            result = self.run_command(str(AUDITOR), str(root))
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_unicode_task_ids_match_the_complete_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            for name in ('PROGRESS.md', 'TODO.md'):
                path = root / name
                path.write_text(path.read_text(encoding='utf-8').replace('T-001', 'R8-校验-长任务名称'),
                                encoding='utf-8')
            self.assertNotIn('NEXT_TASK_ID_MISSING', self.codes(root))
            self.assertNotIn('NEXT_TASK_NOT_ACTIVE', self.codes(root))
            path = root / 'PROGRESS.md'
            path.write_text(path.read_text(encoding='utf-8').replace('R8-校验-长任务名称', 'R8-校验-不存在'),
                            encoding='utf-8')
            self.assertIn('NEXT_TASK_NOT_ACTIVE', self.codes(root))

    def test_phase_ids_are_not_substring_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            path = root / 'PROGRESS.md'
            path.write_text(path.read_text(encoding='utf-8').replace('Current Phase: S1', 'Current Phase: S10'),
                            encoding='utf-8')
            self.assertIn('PHASE_PLAN_MISMATCH', self.codes(root))

    def test_final_status_column_is_supported_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            path = root / 'TODO.md'
            path.write_text(path.read_text(encoding='utf-8').replace('| Status |', '| Final Status |'),
                            encoding='utf-8')
            self.assertNotIn('TASK_TABLE_MISSING', self.codes(root))

    def test_fenced_examples_are_not_live_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            path = root / 'TODO.md'
            example = '```markdown\n| ID | Status |\n| --- | --- |\n| T-999 | Done |\n```\n\n'
            path.write_text(example + path.read_text(encoding='utf-8'), encoding='utf-8')
            self.assertNotIn('TERMINAL_TASK_ACTIVE', self.codes(root))
            self.assertNotIn('NEXT_TASK_NOT_ACTIVE', self.codes(root))

    def test_bad_layout_config_does_not_silently_fall_back(self):
        for cfg in ({'documents': {'typo_role': 'TODO.md'}},
                    {'task_archive_globs': ['../outside/*.md']},
                    {'documents': []}, {'thresholds': {'progress_stale_days': -1}}):
            with self.subTest(cfg=cfg), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.make_base_project(root)
                self.write(root, 'projectos.audit.json', json.dumps(cfg))
                result = self.run_command(str(AUDITOR), str(root))
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
