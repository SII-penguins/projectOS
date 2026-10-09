"""Project enrollment and real command I/O; no Codex host is launched here."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_host_adapter as helpers

hook = helpers.hook


class ProjectScopeHookTest(unittest.TestCase):
    call = helpers.HostAdapterTest.call
    lose_task = helpers.HostAdapterTest.lose_task

    def setUp(self):
        helpers.HostAdapterTest.setUp(self)
        self.profile.pop("allowed_sessions")
        self.profile["session_scope"] = "project"

    def test_new_sessions_join_without_profile_writes_and_keep_separate_state(self):
        before = copy.deepcopy(self.profile)
        for sid in ("first-session", "future-session"):
            self.assertIn("hookSpecificOutput", self.call("SessionStart", session_id=sid))
            self.call("PreToolUse", session_id=sid)
            self.call("PostToolUse", session_id=sid)
            self.assertNotIn("decision", self.call("Stop", session_id=sid))
            key = hashlib.sha256((sid + "\0eval-turn-1").encode()).hexdigest()
            self.assertTrue((self.state / (key + ".before.json")).is_file())
            self.assertTrue((self.state / (key + ".receipt.json")).is_file())
        self.assertEqual(len(list(self.state.glob("*.receipt.json"))), 2)
        self.assertEqual(self.profile, before)

    def test_plain_subdirectory_is_in_scope(self):
        child = self.root / "src" / "module"
        child.mkdir(parents=True)
        self.call("PreToolUse", session_id="new", cwd=str(child))
        self.assertEqual(len(list(self.state.glob("*.before.json"))), 1)

    def test_other_roots_and_nested_git_boundaries_do_not_read_owners(self):
        sibling = self.base / "project-other"
        sibling.mkdir()
        repo = self.root / "nested-repo"
        (repo / ".git").mkdir(parents=True)
        worktree = self.root / "nested-worktree"
        worktree.mkdir()
        (worktree / ".git").write_text("gitdir: /not-read-by-hook")
        subdir = worktree / "src"
        subdir.mkdir()
        with patch.object(hook.transition, "capture", side_effect=AssertionError("must not read owners")):
            for cwd in (self.base, sibling, repo, worktree, subdir):
                for event in ("SessionStart", "PreToolUse", "PostToolUse", "Stop"):
                    with self.subTest(cwd=cwd, event=event):
                        self.assertEqual(self.call(event, cwd=str(cwd)), {})
        self.assertEqual(list(self.state.iterdir()), [])

    def test_symlink_escape_is_ignored(self):
        outside = self.base / "outside"
        outside.mkdir()
        link = self.root / "escape"
        link.symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.call("PreToolUse", cwd=str(link)), {})
        self.assertEqual(list(self.state.iterdir()), [])

    def test_root_can_itself_be_a_git_worktree(self):
        (self.root / ".git").write_text("gitdir: /not-read-by-hook")
        self.call("PreToolUse")
        self.assertEqual(len(list(self.state.glob("*.before.json"))), 1)

    def test_excluded_session_is_ignored_before_path_access(self):
        self.profile["excluded_sessions"] = ["protected-session"]
        with patch.object(Path, "resolve", side_effect=AssertionError("must not access paths")):
            for event in ("SessionStart", "PreToolUse", "PostToolUse", "Stop"):
                self.assertEqual(self.call(event, session_id="protected-session"), {})
        self.assertEqual(list(self.state.iterdir()), [])

    def test_invalid_identity_never_creates_shared_state(self):
        for sid in (None, "", "  ", [], 1):
            with self.subTest(sid=sid):
                self.assertEqual(self.call("PreToolUse", session_id=sid), {})
        self.assertEqual(list(self.state.iterdir()), [])

    def test_project_scope_cannot_grant_continuation(self):
        for changes in ({"mode": "bounded"}, {"authorized_write_turns": ["eval-turn-1"]},
                        {"allowed_sessions": ["isolated-eval"]}):
            with self.subTest(changes=changes):
                profile = {**self.profile, **changes}
                with self.assertRaises(ValueError):
                    hook.run(profile, self.event)
        self.assertEqual(list(self.state.iterdir()), [])

    def test_invalid_scope_and_exclusions_fail_before_capture(self):
        for changes in ({"session_scope": "all"}, {"excluded_sessions": ["*"]},
                        {"excluded_sessions": "session"}, {"excluded_sessions": [None]}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                hook.run({**self.profile, **changes}, self.event)
        self.assertEqual(list(self.state.iterdir()), [])

    def test_observation_reports_loss_without_mutating_project(self):
        self.call("PreToolUse")
        self.lose_task()
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = self.call("Stop")
        self.assertIn("TASK_DISAPPEARED", result["systemMessage"])
        self.assertNotIn("decision", result)
        self.assertEqual({p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}, before)

    def test_missed_baseline_stays_unverified(self):
        self.call("PostToolUse")
        self.assertIn("unchecked", self.call("PreToolUse")["hookSpecificOutput"]["additionalContext"])
        self.assertIn("unchecked", self.call("Stop")["systemMessage"])
        self.assertEqual(list(self.state.glob("*.before.json")), [])

    def test_project_sessions_still_require_real_turn_identity(self):
        result = self.call("PreToolUse", turn_id=None)
        self.assertIn("unchecked", result["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(list(self.state.iterdir()), [])

    def test_existing_allowlist_mode_remains_opt_in(self):
        self.profile.pop("session_scope")
        self.assertEqual(self.call("PreToolUse"), {})
        self.profile["allowed_sessions"] = ["isolated-eval"]
        self.call("PreToolUse")
        self.assertEqual(len(list(self.state.glob("*.before.json"))), 1)
        self.assertEqual(self.call("PreToolUse", session_id="future-session"), {})

    def test_command_accepts_two_future_sessions_with_unchanged_profile(self):
        profile = self.base / "profile.json"
        profile.write_text(json.dumps(self.profile))
        original = profile.read_bytes()
        command = [sys.executable, "-B", str(helpers.fixtures.SKILL_ROOT / "scripts/projectos_hook.py"),
                   "--profile", str(profile)]
        for sid in ("first-process-session", "future-process-session"):
            for name in ("SessionStart", "PreToolUse", "PostToolUse", "Stop"):
                event = {**self.event, "session_id": sid, "hook_event_name": name}
                result = subprocess.run(command, input=json.dumps(event), text=True, capture_output=True, check=True)
                output = json.loads(result.stdout)
                self.assertNotIn("decision", output)
                if name == "SessionStart":
                    self.assertIn("additionalContext", output["hookSpecificOutput"])
                if name == "Stop":
                    self.assertIn("ProjectOS transition", output["systemMessage"])
                    self.assertNotIn("unchecked", output["systemMessage"])
        self.assertEqual(profile.read_bytes(), original)
        self.assertEqual(len(list(self.state.glob("*.receipt.json"))), 2)


if __name__ == "__main__":
    unittest.main()
