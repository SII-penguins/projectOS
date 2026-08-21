#!/usr/bin/env python3
"""Regression tests for ProjectOS lifecycle tooling."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_skill.py"
AUDITOR = SKILL_ROOT / "scripts" / "audit_project_docs.py"
TODAY = "2026-08-21"

COMMON = """\
Status: Active
Canonical For: {owner}
Last Reconciled: 2026-08-21
Freshness Rule: Reconcile on every owner-specific change.
Archive Rule: Promote durable facts before moving terminal history to doc/archive/.
"""


class ProjectOSToolsTest(unittest.TestCase):
    def run_command(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], check=False, text=True, capture_output=True)

    def write(self, root: Path, relative: str, content: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

    def make_base_project(self, root: Path) -> None:
        self.write(
            root,
            "AGENTS.md",
            COMMON.format(owner="AI routing rules, document map, read order, and completion standard")
            + "\n# AGENTS.md\n\nRead PROGRESS.md, then TODO.md.\n",
        )
        self.write(
            root,
            "PROGRESS.md",
            COMMON.format(owner="Current live state, trusted resume point, blocker, and next action")
            + """
As Of: 2026-08-21
Current Phase: S1
Next Action: Execute `T-001` after confirming its acceptance gate.

# Current Live Status

No blocker.
""",
        )
        self.write(
            root,
            "TODO.md",
            COMMON.format(owner="Current active task queue, dependencies, ownership, and acceptance gates")
            + """
# Active Queue

| ID | Status | Owner | Scope | Dependencies | Next Action | Acceptance Gate | Evidence | Last Touched |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-001 | Ready | main-agent | Implement one bounded change | None | Run focused check | Check passes | Pending | 2026-08-21 |
""",
        )
        self.write(
            root,
            "doc/IMPLEMENTATION_PLAN.md",
            COMMON.format(owner="Roadmap, accepted phase history, stage gates, and exit criteria")
            + """
Plan Version: 1.0.0

# Master Roadmap

| Stage | Goal | Entry | Exit | Artifacts | Boundary | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Build bounded feature | Brief approved | Focused check passes | Evidence log | No scope expansion | Active |
""",
        )

    def audit_json(self, root: Path, *extra: str) -> dict:
        result = self.run_command(
            str(AUDITOR), str(root), "--today", TODAY, "--format", "json", "--fail-on", "none", *extra
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_skill_package_validates(self) -> None:
        result = self.run_command(str(VALIDATOR), str(SKILL_ROOT))
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("0 error(s)", result.stdout)

    def test_clean_minimal_project_has_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            payload = self.audit_json(root)
            self.assertEqual(payload["findings"], [], msg=json.dumps(payload, indent=2))

    def test_audit_detects_terminal_task_and_cross_document_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            progress = (root / "PROGRESS.md").read_text(encoding="utf-8")
            progress = progress.replace("Current Phase: S1", "Current Phase: S2").replace("`T-001`", "`T-999`")
            (root / "PROGRESS.md").write_text(progress, encoding="utf-8")
            todo = (root / "TODO.md").read_text(encoding="utf-8").replace("| T-001 | Ready |", "| T-001 | Done |")
            (root / "TODO.md").write_text(todo, encoding="utf-8")
            codes = {finding["code"] for finding in self.audit_json(root)["findings"]}
            self.assertIn("TERMINAL_TASK_ACTIVE", codes)
            self.assertIn("NEXT_TASK_NOT_ACTIVE", codes)
            self.assertIn("PHASE_PLAN_MISMATCH", codes)

    def test_archive_shadow_queue_and_progress_bloat_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            progress = (root / "PROGRESS.md").read_text(encoding="utf-8")
            progress += "\n" + "\n".join(f"Historical note {index}" for index in range(280)) + "\n"
            (root / "PROGRESS.md").write_text(progress, encoding="utf-8")
            self.write(
                root,
                "doc/archive/TASKS.md",
                COMMON.format(owner="Terminal task outcomes and retained closeout evidence")
                + """
# Terminal Task Archive

| ID | Status | Closed On | Evidence | Outcome |
| --- | --- | --- | --- | --- |
| T-099 | Blocked |  | pending | waiting for approval |
| T-001 | Done | 2026-08-21 | tests/pass.txt | accepted |
""",
            )
            codes = {finding["code"] for finding in self.audit_json(root)["findings"]}
            self.assertIn("PROGRESS_TOO_LARGE", codes)
            self.assertIn("ARCHIVE_ACTIVE_TASK", codes)
            self.assertIn("TASK_ACTIVE_AND_ARCHIVED", codes)

    def test_closeout_fixture_is_compact_and_has_active_only_todo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(
                root,
                "TODO.md",
                COMMON.format(owner="Current active task queue, dependencies, ownership, and acceptance gates")
                + """
# Active Queue

| ID | Status | Owner | Scope | Dependencies | Next Action | Acceptance Gate | Evidence | Last Touched |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-002 | Ready | main-agent | Continue the accepted stage | T-001 archived | Run successor check | Successor check passes | Pending | 2026-08-21 |
""",
            )
            self.write(
                root,
                "PROGRESS.md",
                COMMON.format(owner="Current live state, trusted resume point, blocker, and next action")
                + """
As Of: 2026-08-21
Current Phase: S1
Next Action: Execute `T-002` using the accepted T-001 evidence.

# Current Live Status

T-001 passed and was archived. No blocker remains.
""",
            )
            self.write(
                root,
                "doc/archive/TASKS.md",
                COMMON.format(owner="Terminal task outcomes and retained closeout evidence")
                + """
# Terminal Task Archive

| ID | Status | Closed On | Evidence | Outcome |
| --- | --- | --- | --- | --- |
| T-001 | Done | 2026-08-21 | tests/pass.txt | Accepted; successor T-002 opened |
""",
            )
            payload = self.audit_json(root)
            codes = {finding["code"] for finding in payload["findings"]}
            forbidden = {
                "TERMINAL_TASK_ACTIVE", "ARCHIVE_ACTIVE_TASK", "TASK_ACTIVE_AND_ARCHIVED",
                "PROGRESS_TOO_LARGE", "NEXT_TASK_NOT_ACTIVE",
            }
            self.assertTrue(forbidden.isdisjoint(codes), msg=json.dumps(payload, indent=2))
            self.assertLess(len((root / "PROGRESS.md").read_text(encoding="utf-8").splitlines()), 250)
            todo_text = (root / "TODO.md").read_text(encoding="utf-8")
            self.assertNotIn("| Done |", todo_text)
            self.assertIn("| T-002 | Ready |", todo_text)

    def test_other_document_lifecycle_findings_are_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            self.write(
                root, "doc/PRD.md",
                COMMON.format(owner="Product goal, scope, success metrics, and claim boundaries")
                + "\n# PRD\n\nCurrent blocker: unclear market.\n",
            )
            self.write(
                root, "doc/diagnostics/2026-08-21-test.md",
                COMMON.format(owner="Failure analysis and retained diagnostic evidence")
                + "\n# Diagnosis\n\nObserved facts.\n",
            )
            self.write(
                root, "doc/TEAM.md",
                COMMON.format(owner="Stable collaboration roles, permissions, concurrency, and handoff protocol")
                + "\n# TEAM\n\nCurrent assignee: agent-a.\n",
            )
            self.write(
                root, "lessons.md",
                COMMON.format(owner="Real mistakes, causes, corrections, and prevention rules")
                + """
# Lessons

## 2026-08-21 - Example
Mistake: stale state.
Cause: no closeout.
Correction: reconcile.
Future rule: close out tasks.
""",
            )
            codes = {finding["code"] for finding in self.audit_json(root)["findings"]}
            for expected in (
                "CONTRACT_VERSION_MISSING", "CONTRACT_VERIFICATION_MISSING", "CONTRACT_LIVE_POLLUTION",
                "DIAGNOSTIC_STATUS_MISSING", "TEAM_ROSTER_POLLUTION", "LESSON_RULE_STATUS_PARTIAL",
            ):
                self.assertIn(expected, codes)

    def test_custom_document_map_supports_existing_nonstandard_repos(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write(
                root,
                "projectos.audit.json",
                json.dumps({
                    "documents": {
                        "entrypoint": "00/AGENTS.md", "progress": "00/PROGRESS.md",
                        "todo": "02/TODO.md", "plan": "02/IMPLEMENTATION_PLAN.md",
                    },
                    "active_task_statuses": ["approval-blocked"],
                    "task_archive_globs": ["02/archive/*.md"],
                }),
            )
            self.write(root, "00/AGENTS.md", COMMON.format(owner="AI routing rules and canonical document map") + "\n# AGENTS\n")
            self.write(
                root, "00/PROGRESS.md",
                COMMON.format(owner="Current phase, blocker, evidence summary, and resume action")
                + """
As Of: 2026-08-21
Current Phase: R8
Next Action: Await approval for `R8-DIAG`.
""",
            )
            self.write(
                root, "02/TODO.md",
                COMMON.format(owner="Current active task queue and acceptance gates")
                + """
| ID | Status | Owner | Dependencies | Next Action | Acceptance Gate | Evidence | Last Touched |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R8-DIAG | approval-blocked | agent | user approval | wait | approval received | pending | 2026-08-21 |
""",
            )
            self.write(
                root, "02/IMPLEMENTATION_PLAN.md",
                COMMON.format(owner="Roadmap, phase history, stage gates, and fallback rules")
                + """
Plan Version: 1.0.0
| Stage | Goal | Entry | Exit | Artifacts | Boundary | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R8 | Diagnose | R7 complete | decision | report | read-only | Active |
""",
            )
            payload = self.audit_json(root)
            unknown = [finding for finding in payload["findings"] if finding["code"] == "TASK_STATUS_UNKNOWN"]
            self.assertEqual(unknown, [], msg=json.dumps(payload, indent=2))
            self.assertIsNotNone(payload["config"])

    def test_audit_never_edits_the_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_base_project(root)
            before = {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            result = self.run_command(str(AUDITOR), str(root), "--today", TODAY, "--fail-on", "none")
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            after = {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
