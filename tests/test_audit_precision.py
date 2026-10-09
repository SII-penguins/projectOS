"""Positive and negative cases for Markdown scope and evidence precision."""

import json
from pathlib import Path
import tempfile
import unittest

import test_projectos_tools as fixtures

AUDITOR, COMMON = fixtures.AUDITOR, fixtures.COMMON


class AuditPrecisionTest(unittest.TestCase):
    write = fixtures.ProjectOSToolsTest.write
    make_base_project = fixtures.ProjectOSToolsTest.make_base_project
    run_command = fixtures.ProjectOSToolsTest.run_command
    audit_json = fixtures.ProjectOSToolsTest.audit_json

    def codes(self, root):
        return {f["code"] for f in self.audit_json(root)["findings"]}

    def test_nested_section_inherits_only_document_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(root, "AGENTS.md", COMMON.format(owner="routing"))
            self.write(
                root,
                "PROJECT.md",
                "# Project\n" + COMMON.format(owner="section owners") + """

## Old notes
| ID | Status |
| --- | --- |
| T-099 | Done |

## Project work
### Queue
| ID | Status | Owner | Dependencies | Next Action | Acceptance Gate | Evidence | Last Touched |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-001 | Ready | main | None | Check | Passes | Pending | 2026-08-21 |
""",
            )
            self.write(
                root,
                "projectos.audit.json",
                json.dumps({"documents": {"todo": {"path": "PROJECT.md", "section": "Queue"}}}),
            )
            payload = self.audit_json(root)
            self.assertEqual(payload["findings"], [])
            self.assertEqual(payload["coverage"]["active_task_rows"], 1)

    def test_hash_in_heading_name_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(
                root,
                "PROJECT.md",
                COMMON.format(owner="tasks") + "\n## C#\n| ID | Status |\n| --- | --- |\n",
            )
            self.write(
                root,
                "projectos.audit.json",
                json.dumps({"documents": {"todo": {"path": "PROJECT.md", "section": "C#"}}}),
            )
            self.assertNotIn("TASK_TABLE_MISSING", self.codes(root))

    def test_link_destination_is_not_a_task_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(
                root,
                "doc/archive/TASKS.md",
                COMMON.format(owner="terminal outcomes")
                + "\n| ID | Status | Evidence |\n| --- | --- | --- |\n| T-099 | Done | check.log |\n",
            )
            p = root / "TODO.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    "| None |", "| [T-099](doc/archive/RELEASE-OLD.md) |"
                ),
                encoding="utf-8",
            )
            self.assertNotIn("DEPENDENCY_UNKNOWN", self.codes(root))

    def test_trust_glossary_does_not_validate_run_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(
                root,
                "doc/RUN_REGISTRY.md",
                COMMON.format(owner="run facts") + """
## Trust glossary
| Trust | Meaning |
| --- | --- |
| smoke | limited validation |

## Runs
| ID | Output | Outcome |
| --- | --- | --- |
| R-001 | result.log | finished |
""",
            )
            self.assertIn("RUN_TRUST_MISSING", self.codes(root))

    def test_run_rows_need_identity_and_trust(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(
                root,
                "doc/RUN_REGISTRY.md",
                COMMON.format(owner="run facts")
                + "\n| ID | Trust |\n| --- | --- |\n| R-001 | |\n| R-001 | smoke |\n| | diagnostic |\n",
            )
            codes = self.codes(root)
            self.assertIn("RUN_TRUST_EMPTY", codes)
            self.assertIn("RUN_ID_DUPLICATE", codes)
            self.assertIn("RUN_ID_MISSING", codes)

    def test_archived_attempt_cannot_have_empty_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(
                root,
                "doc/archive/TASKS.md",
                COMMON.format(owner="terminal outcomes")
                + "\n| ID | Status | Evidence |\n| --- | --- | --- |\n| | Done | pass.log |\n",
            )
            self.assertIn("ARCHIVE_ID_MISSING", self.codes(root))

    def test_missing_active_stage_is_reported_for_active_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            p = root / "doc/IMPLEMENTATION_PLAN.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace("| Active |", "| Completed |"),
                encoding="utf-8",
            )
            self.assertIn("NO_ACTIVE_STAGE", self.codes(root))
            p = root / "PROGRESS.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace("Current Phase: S1", "Current Phase: S9"),
                encoding="utf-8",
            )
            self.assertIn("PHASE_NOT_FOUND", self.codes(root))

    def test_closed_roadmap_and_empty_queue_are_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            p = root / "doc/IMPLEMENTATION_PLAN.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace("| Active |", "| Completed |"),
                encoding="utf-8",
            )
            p = root / "TODO.md"
            p.write_text(
                "\n".join(
                    line
                    for line in p.read_text(encoding="utf-8").splitlines()
                    if not line.startswith("| T-001 |")
                ),
                encoding="utf-8",
            )
            p = root / "PROGRESS.md"
            p.write_text(
                p.read_text(encoding="utf-8").replace(
                    "Next Action: Execute `T-001` after confirming its acceptance gate.",
                    "Next Task: None\nNext Action: Closed.",
                ),
                encoding="utf-8",
            )
            self.assertEqual(self.audit_json(root)["findings"], [])

    def test_blocked_queue_preserves_partial_stage_without_false_activity_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            plan = root / "doc/IMPLEMENTATION_PLAN.md"
            plan.write_text(plan.read_text().replace("| Active |", "| Partial |"))
            todo = root / "TODO.md"
            todo.write_text(todo.read_text().replace("| Ready |", "| Blocked |"))
            before = {str(p): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertNotIn("NO_ACTIVE_STAGE", self.codes(root))
            self.assertEqual(before, {str(p): p.read_bytes() for p in root.rglob('*') if p.is_file()})
            # Partial acceptance cannot excuse an actually Ready queue with no
            # executing stage, nor an entirely completed roadmap with open work.
            todo.write_text(todo.read_text().replace("| Blocked |", "| Ready |"))
            self.assertIn("NO_ACTIVE_STAGE", self.codes(root))
            todo.write_text(todo.read_text().replace("| Ready |", "| Blocked |"))
            plan.write_text(plan.read_text().replace("| Partial |", "| Completed |"))
            self.assertIn("NO_ACTIVE_STAGE", self.codes(root))

    def test_partial_upstream_and_active_downstream_are_not_two_executing_stages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            plan = root / "doc/IMPLEMENTATION_PLAN.md"
            plan.write_text(plan.read_text() + "\n| Stage | Status |\n| --- | --- |\n| S0 | Partial |\n")
            self.assertNotIn("MULTIPLE_ACTIVE_STAGES", self.codes(root))

    def test_unrelated_partial_stage_cannot_hide_closed_current_stage_with_open_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            plan = root / "doc/IMPLEMENTATION_PLAN.md"
            plan.write_text(plan.read_text().replace("| Active |", "| Completed |")
                            + "\n| Stage | Status |\n| --- | --- |\n| S0 | Partial |\n")
            todo = root / "TODO.md"
            todo.write_text(todo.read_text().replace("| Ready |", "| Blocked |"))
            self.assertIn("NO_ACTIVE_STAGE", self.codes(root))

    def test_ambiguous_current_identity_cannot_supply_waiting_exemption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            plan = root / "doc/IMPLEMENTATION_PLAN.md"
            original = plan.read_text()
            todo = root / "TODO.md"
            todo.write_text(todo.read_text().replace("| Ready |", "| Blocked |"))
            for current_status in ("Completed", "Partial"):
                plan.write_text(original.replace("| Active |", f"| {current_status} |")
                                + "\n| Stage | Status |\n| --- | --- |\n| S1 historical | Partial |\n")
                codes = self.codes(root)
                self.assertIn("NO_ACTIVE_STAGE", codes)
                self.assertIn("PHASE_IDENTITY_AMBIGUOUS", codes)

    def test_duplicate_configuration_keys_fail_visibly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(root, "projectos.audit.json", '{"documents":{"todo":"TODO.md","todo":null}}')
            result = self.run_command(str(AUDITOR), str(root))
            self.assertEqual(result.returncode, 2)

    def test_explicitly_disabled_entrypoint_is_not_a_missing_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(
                root, "projectos.audit.json", json.dumps({"documents": {"entrypoint": None}})
            )
            payload = self.audit_json(root)
            self.assertEqual(payload["findings"], [])
            self.assertNotIn("entrypoint", {d["role"] for d in payload["coverage"]["documents"]})

    def test_report_io_error_uses_documented_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "project"
            self.make_base_project(root)
            output = parent / "report-directory"
            output.mkdir()
            result = self.run_command(str(AUDITOR), str(root), "--output", str(output))
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("Traceback", result.stderr)

    def test_empty_normalized_status_alias_cannot_accept_empty_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(root, "projectos.audit.json", json.dumps({"terminal_task_statuses": ["**"]}))
            result = self.run_command(str(AUDITOR), str(root))
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
