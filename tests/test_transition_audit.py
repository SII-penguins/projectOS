"""Behavioral contracts for read-only document transitions (not model trials)."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import test_projectos_tools as fixtures
sys.path.insert(0, str(fixtures.SKILL_ROOT / "scripts"))
import audit_project_docs as audit
import audit_project_transition as transition

EXIT_TABLE = """
## Exit obligations
| Exit ID | Requirement | Status | Tasks | Decision | Owner | Revisit |
| --- | --- | --- | --- | --- | --- | --- |
| S1-G1 | Check passes | Open | T-001 | | lead | |
"""


class TransitionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "project"
        self.root.mkdir()
        fixtures.ProjectOSToolsTest().make_base_project(self.root)
        self.plan = self.root / "doc/IMPLEMENTATION_PLAN.md"
        self.plan.write_text(self.plan.read_text() + EXIT_TABLE)
        self.before = transition.capture(self.root)

    def edit(self, name, old, new):
        path = self.root / name
        path.write_text(path.read_text().replace(old, new))

    def report(self):
        return transition.compare(self.before, transition.capture(self.root))

    def codes(self):
        return {x["code"] for x in self.report()["findings"]}

    def drop_task(self):
        path = self.root / "TODO.md"
        path.write_text("\n".join(x for x in path.read_text().splitlines() if not x.startswith("| T-001 |")) + "\n")

    def archive(self, status="Done", evidence="check.log"):
        p = self.root / "doc/archive/TASKS.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("| ID | Status | Evidence |\n| --- | --- | --- |\n| T-001 | " + status + " | " + evidence + " |\n")

    def test_unchanged_supported_state_checked_and_no_writes(self):
        hashes = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(self.report()["status"], "checked")
        self.assertEqual(hashes, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_task_and_all_references_removed_still_detected(self):
        self.drop_task()
        self.plan.write_text(self.plan.read_text().replace(EXIT_TABLE, ""))
        self.assertIn("TASK_DISAPPEARED", self.codes())
        self.assertIn("EXIT_DISAPPEARED", self.codes())

    def test_same_id_weakened_acceptance_requires_review(self):
        self.edit("TODO.md", "Check passes", "File exists")
        self.assertIn("ACCEPTANCE_CHANGED_REVIEW", self.codes())

    def test_requirement_change_cannot_hide_behind_stable_exit_id(self):
        self.edit("doc/IMPLEMENTATION_PLAN.md", "| Check passes | Open", "| File exists | Open")
        self.assertIn("EXIT_REQUIREMENT_CHANGED_REVIEW", self.codes())

    def test_downstream_pass_does_not_close_upstream(self):
        self.drop_task()
        self.archive()
        self.assertIn("EXIT_TASK_NOT_ACTIVE", self.codes())

    def test_archive_unknown_status_not_terminal(self):
        self.drop_task()
        self.archive("almost passed")
        self.assertIn("NONTERMINAL_ARCHIVED", self.codes())

    def test_terminal_needs_nonempty_outcome(self):
        self.drop_task()
        self.archive(evidence="TBD")
        self.assertIn("TERMINAL_OUTCOME_UNVERIFIED", self.codes())

    def test_legitimate_completion_still_requires_scope_review(self):
        self.drop_task()
        self.archive()
        self.edit("doc/IMPLEMENTATION_PLAN.md", "| Open | T-001 | |", "| Satisfied | T-001 | check.log |")
        report = self.report()
        self.assertEqual(report["status"], "review_required")
        self.assertFalse(any(f["severity"] == "ERROR" for f in report["findings"]))

    def test_deferral_requires_owner_and_event(self):
        self.edit("doc/IMPLEMENTATION_PLAN.md", "| Open | T-001 | | lead | |", "| Deferred | | decision.md | | |")
        self.assertIn("EXIT_TRACKING_MISSING", self.codes())

    def test_deferral_reference_is_not_approval_proof(self):
        self.edit("doc/IMPLEMENTATION_PLAN.md", "| Open | T-001 | | lead | |", "| Deferred | | decision.md | lead | approval arrives |")
        self.assertEqual(self.report()["status"], "review_required")
        self.assertIn("approval authenticity", self.report()["coverage"]["not_checked"])

    def test_missing_task_structure_never_passes(self):
        (self.root / "TODO.md").write_text("Tasks are in a proprietary system.\n")
        self.assertFalse(self.report()["coverage"]["task_destinations"])
        self.assertNotEqual(self.report()["status"], "checked")

    def test_unrecognized_acceptance_column_is_partial_not_checked(self):
        self.edit("TODO.md", "Acceptance Gate", "Opaque gate")
        self.before = transition.capture(self.root)
        report = self.report()
        self.assertEqual(report["status"], "partial")
        self.assertFalse(report["coverage"]["acceptance_changes"])

    def test_missing_exit_schema_is_partial(self):
        self.plan.write_text(self.plan.read_text().replace(EXIT_TABLE, ""))
        self.before = transition.capture(self.root)
        self.assertEqual(self.report()["status"], "partial")

    def test_unknown_task_status_does_not_allow_disappearance(self):
        self.edit("TODO.md", "| Ready |", "| needs-author |")
        self.before = transition.capture(self.root)
        self.drop_task()
        self.assertIn("TASK_DISAPPEARED", self.codes())

    def test_history_cannot_disappear(self):
        self.archive()
        self.drop_task()
        self.before = transition.capture(self.root)
        (self.root / "doc/archive/TASKS.md").unlink()
        self.assertIn("HISTORY_DISAPPEARED", self.codes())

    def test_duplicate_attempt_is_ambiguous(self):
        self.archive()
        self.assertIn("TRANSITION_TASK_DUPLICATE", self.codes())

    def test_capture_does_not_read_unrelated_diagnostic_history(self):
        p = self.root / "doc/diagnostics/large-history.md"
        p.parent.mkdir()
        p.write_bytes(b"\xffnot utf8")
        snapshot = transition.capture(self.root)
        self.assertNotIn("doc/diagnostics/large-history.md", snapshot["files"])

    def test_interrupted_identical_terminal_copy_can_finish_without_duplicate_error(self):
        self.edit("TODO.md", "| Ready |", "| Done |")
        self.edit("TODO.md", "| Pending |", "| check.log |")
        self.edit("doc/IMPLEMENTATION_PLAN.md", "| Open | T-001 | |", "| Satisfied | T-001 | check.log |")
        self.archive()
        self.before = transition.capture(self.root)
        self.drop_task()
        report = self.report()
        self.assertNotIn("TRANSITION_TASK_DUPLICATE", {x["code"] for x in report["findings"]})
        self.assertEqual(report["resolved_baseline_duplicates"], ["T-001"])

    def test_conflicting_baseline_duplicate_still_needs_review(self):
        self.archive()
        self.before = transition.capture(self.root)
        self.drop_task()
        self.assertIn("BASELINE_DUPLICATE_REVIEW", self.codes())

    def test_worktree_mismatch_rejected(self):
        other = copy.deepcopy(self.before)
        other["project_root"] += "-other"
        with self.assertRaisesRegex(ValueError, "different root"):
            transition.compare(other, transition.capture(self.root))

    def test_corrupted_snapshot_rejected(self):
        before = copy.deepcopy(self.before)
        before["roles"]["todo"]["text"] = "forged"
        p = Path(self.tmp.name) / "before.json"
        p.write_text(json.dumps(before))
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            transition.load_snapshot(p)

    def test_cli_guard_rejects_concurrent_edit_and_compare_is_read_only(self):
        p = Path(self.tmp.name) / "before.json"
        p.write_text(json.dumps(self.before))
        tool = fixtures.SKILL_ROOT / "scripts/audit_project_transition.py"
        args = [sys.executable, "-B", str(tool), "guard", str(self.root), "--before", str(p)]
        self.assertEqual(subprocess.run(args, capture_output=True).returncode, 0)
        self.edit("TODO.md", "Check passes", "Changed gate")
        self.assertEqual(subprocess.run(args, capture_output=True).returncode, 1)
        result = subprocess.run([sys.executable, "-B", str(tool), "compare", str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "unchecked")

    def test_config_change_cannot_silently_disable_coverage(self):
        (self.root / "projectos.audit.json").write_text(json.dumps({"documents": {"plan": None}}))
        self.assertIn("CONFIG_CHANGED_REVIEW", self.codes())


class MaintenancePrecisionTest(unittest.TestCase):
    def test_duplicate_same_scope_conflicts_but_history_does_not(self):
        current = "Current Phase: S1\nCurrent Phase: S2\n"
        codes = {x["code"] for x in audit.duplicate_current_fields(Path("PROGRESS.md"), current, Path("."))}
        self.assertIn("CURRENT_FIELD_CONFLICT", codes)
        separated = "# Project\n## Current\nCurrent Phase: S2\n## History\nCurrent Phase: S1\n"
        self.assertEqual(audit.duplicate_current_fields(Path("PROGRESS.md"), separated, Path(".")), [])

    def test_combined_view_excludes_historical_duplicate(self):
        text = "## Current\nCurrent Phase: S1\n## History\nCurrent Phase: S2\nCurrent Phase: S3\n"
        view = audit.select_section(text, "Current")
        self.assertEqual(audit.duplicate_current_fields(Path("P.md"), view, Path(".")), [])

    def test_fenced_duplicates_are_examples(self):
        text = "Current Phase: S1\n```\nCurrent Phase: S2\n```\n"
        self.assertEqual(audit.duplicate_current_fields(Path("P.md"), text, Path(".")), [])

    def test_evidence_three_states_and_custom_alias(self):
        def record(column, value, config=None):
            text = f"| ID | Status | {column} |\n| --- | --- | --- |\n| T-001 | Done | {value} |\n"
            return next(audit.task_records("a.md", text, config))
        self.assertEqual(record("Unknown format", "check.log")["evidence_state"], "unsupported")
        self.assertEqual(record("Evidence", "")["evidence_state"], "empty")
        self.assertEqual(record("Scope and evidence", "check.log")["evidence_state"], "present_unverified")
        self.assertEqual(record("Proof", "check.log", {"evidence_columns": ["Proof"]})["evidence_state"], "present_unverified")

    def test_cancellation_decision_not_hidden_by_empty_evidence_column(self):
        text = "| ID | Status | Evidence | Decision |\n| --- | --- | --- | --- |\n| T-001 | Cancelled | | decision.md |\n"
        rec = next(audit.task_records("a.md", text))
        self.assertEqual(rec["evidence_state"], "present_unverified")
        self.assertEqual(rec["evidence"], "decision.md")

    def test_unknown_column_warning_differs_from_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / "doc/archive/TASKS.md"
            p.parent.mkdir(parents=True)
            p.write_text("| ID | Status | Legacy note |\n| --- | --- | --- |\n| T-001 | Done | check.log |\n")
            import datetime
            codes = {x["code"] for x in audit.audit(root, datetime.date(2026, 8, 21), {})}
            self.assertIn("ARCHIVE_EVIDENCE_UNSUPPORTED", codes)
            self.assertNotIn("ARCHIVE_EVIDENCE_MISSING", codes)
