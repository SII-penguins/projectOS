"""Event-level adapter tests; these do not launch or modify any Codex session."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
import unittest

import test_projectos_tools as fixtures
sys.path.insert(0, str(fixtures.SKILL_ROOT / "scripts"))
import projectos_hook as hook


class HostAdapterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "project"
        self.root.mkdir()
        fixtures.ProjectOSToolsTest().make_base_project(self.root)
        self.state = self.base / "state"
        self.state.mkdir(mode=0o700)
        self.profile = {"schema": "projectos-hook-v1", "project_root": str(self.root),
                        "state_dir": str(self.state), "allowed_sessions": ["isolated-eval"],
                        "mode": "observe", "authorized_write_turns": []}
        self.event = {"session_id": "isolated-eval", "turn_id": "eval-turn-1", "cwd": str(self.root),
                      "permission_mode": "default", "hook_event_name": "PreToolUse"}

    def call(self, name, **changes):
        return hook.run(self.profile, {**self.event, "hook_event_name": name, **changes})

    def lose_task(self):
        p = self.root / "TODO.md"
        p.write_text("\n".join(x for x in p.read_text().splitlines() if not x.startswith("| T-001 |")))

    def test_other_session_causes_no_reads_or_state(self):
        from unittest.mock import patch
        with patch.object(hook.transition, "capture", side_effect=AssertionError("must not read")):
            self.assertEqual(self.call("PreToolUse", session_id="protected-existing-session"), {})
        self.assertEqual(list(self.state.iterdir()), [])

    def test_other_worktree_ignored(self):
        self.assertEqual(self.call("PreToolUse", cwd=str(self.base)), {})
        self.assertEqual(list(self.state.iterdir()), [])

    def test_startup_and_compaction_context_never_continue(self):
        for source in ("startup", "resume", "compact"):
            result = self.call("SessionStart", source=source)
            self.assertIn("additionalContext", result["hookSpecificOutput"])
            self.assertNotIn("decision", result)
        self.assertEqual(list(self.state.iterdir()), [])

    def test_pretool_baseline_not_overwritten_after_edit(self):
        self.call("PreToolUse")
        path = next(self.state.glob("*.before.json"))
        old = path.read_bytes()
        self.lose_task()
        self.call("PreToolUse")
        self.assertEqual(path.read_bytes(), old)

    def test_overlapping_pretools_capture_only_once(self):
        from unittest.mock import patch
        original = hook.transition.capture
        entered, release, second_started = (threading.Event() for _ in range(3))

        def delayed_capture(*args, **kwargs):
            entered.set()
            if not release.wait(5):
                raise RuntimeError("test did not release capture")
            return original(*args, **kwargs)

        def second_tool():
            second_started.set()
            self.call("PreToolUse")
            self.lose_task()

        with patch.object(hook.transition, "capture", side_effect=delayed_capture) as capture:
            with ThreadPoolExecutor(max_workers=2) as pool:
                first = pool.submit(self.call, "PreToolUse")
                try:
                    self.assertTrue(entered.wait(5))
                    second = pool.submit(second_tool)
                    self.assertTrue(second_started.wait(5))
                finally:
                    release.set()
                first.result(timeout=5)
                second.result(timeout=5)
            self.assertEqual(capture.call_count, 1)
        self.assertIn("TASK_DISAPPEARED", self.call("Stop")["systemMessage"])

    def test_overlapping_stops_continue_once(self):
        self.profile.update(mode="bounded", authorized_write_turns=["eval-turn-1"])
        self.call("PreToolUse")
        self.lose_task()
        start = threading.Barrier(8)

        def stop():
            start.wait(timeout=5)
            return self.call("Stop")

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: stop(), range(8)))
        self.assertEqual(sum(x.get("decision") == "block" for x in results), 1)

    def test_lock_alias_cannot_touch_another_file(self):
        import os
        victim = self.base / "protected-session.jsonl"
        victim.write_text("untouched")
        key = hashlib.sha256(b"isolated-eval\0eval-turn-1").hexdigest()
        lock = self.state / (key + ".lock")
        lock.symlink_to(victim)
        with self.assertRaises(OSError):
            self.call("PreToolUse")
        lock.unlink()
        os.link(victim, lock)
        with self.assertRaises(ValueError):
            self.call("PreToolUse")
        self.assertEqual(victim.read_text(), "untouched")

    def test_posttool_cannot_fabricate_baseline(self):
        self.lose_task()
        result = self.call("PostToolUse")
        self.assertIn("unchecked", result["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(len(list(self.state.glob("*.tainted.json"))), 1)
        self.assertEqual(list(self.state.glob("*.before.json")), [])

    def test_missed_pretool_poison_survives_later_pretool_and_stop(self):
        from unittest.mock import patch
        # The disappeared task is replaced by a structurally valid new identity.
        for name in ("TODO.md", "PROGRESS.md"):
            p = self.root / name
            p.write_text(p.read_text().replace("T-001", "T-002"))
        self.call("PostToolUse")
        with patch.object(hook.transition, "capture", side_effect=AssertionError("must not fabricate baseline")):
            self.assertIn("unchecked", self.call("PreToolUse")["hookSpecificOutput"]["additionalContext"])
            self.assertIn("unchecked", self.call("Stop")["systemMessage"])
        self.assertEqual(list(self.state.glob("*.before.json")), [])

    def test_missing_and_relative_cwd_rejected_before_capture(self):
        from unittest.mock import patch
        for value in (None, "", ".", "child"):
            with patch.object(hook.transition, "capture", side_effect=AssertionError("must not read")):
                with self.assertRaises(ValueError):
                    self.call("PreToolUse", cwd=value)
        self.assertEqual(list(self.state.iterdir()), [])

    def test_observe_reports_lost_work_without_continuation(self):
        self.call("PreToolUse")
        self.lose_task()
        before = (self.root / "TODO.md").read_bytes()
        result = self.call("Stop")
        self.assertIn("TASK_DISAPPEARED", result["systemMessage"])
        self.assertNotIn("decision", result)
        self.assertEqual((self.root / "TODO.md").read_bytes(), before)

    def test_bounded_is_once_only_for_authorized_turn(self):
        self.profile.update(mode="bounded", authorized_write_turns=["eval-turn-1"])
        self.call("PreToolUse")
        self.lose_task()
        self.assertEqual(self.call("Stop")["decision"], "block")
        self.assertNotIn("decision", self.call("Stop"))

    def test_existing_error_does_not_force_unrelated_repair(self):
        self.profile.update(mode="bounded", authorized_write_turns=["eval-turn-1"])
        path = self.root / "PROGRESS.md"
        path.write_text(path.read_text() + "\nCurrent Phase: other\nCurrent Phase: conflict\n")
        self.call("PreToolUse")
        todo = self.root / "TODO.md"
        todo.write_text(todo.read_text() + "\nUnrelated current note.\n")
        result = self.call("Stop")
        self.assertNotIn("decision", result)
        self.assertIn("CURRENT_FIELD_CONFLICT", result["systemMessage"])

    def test_host_continuation_marker_prevents_loop(self):
        self.profile.update(mode="bounded", authorized_write_turns=["eval-turn-1"])
        self.call("PreToolUse")
        self.lose_task()
        self.assertNotIn("decision", self.call("Stop", stop_hook_active=True))

    def test_readonly_or_unlisted_turn_cannot_continue(self):
        self.profile["mode"] = "bounded"
        self.call("PreToolUse")
        self.lose_task()
        self.assertNotIn("decision", self.call("Stop"))

    def test_plan_mode_cannot_continue(self):
        self.profile.update(mode="bounded", authorized_write_turns=["eval-turn-1"])
        self.call("PreToolUse")
        self.lose_task()
        self.assertNotIn("decision", self.call("Stop", permission_mode="plan"))

    def test_missing_baseline_never_continues(self):
        self.profile.update(mode="bounded", authorized_write_turns=["eval-turn-1"])
        self.assertIn("unchecked", self.call("Stop")["systemMessage"])
        self.assertEqual([p.suffix for p in self.state.iterdir()], [".lock"])

    def test_no_changed_owner_does_not_claim_whole_work_verified(self):
        self.call("PreToolUse")
        result = self.call("Stop")
        self.assertNotIn("decision", result)
        self.assertIn("does not verify implementation", result["systemMessage"])

    def test_missing_turn_never_creates_shared_state(self):
        result = self.call("PreToolUse", turn_id=None)
        self.assertIn("unchecked", result["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(list(self.state.iterdir()), [])

    def test_wildcard_authority_rejected(self):
        self.profile["allowed_sessions"] = ["*"]
        with self.assertRaises(ValueError):
            self.call("PreToolUse")

    def test_state_cannot_be_project_or_parent(self):
        self.profile["state_dir"] = str(self.root)
        with self.assertRaises(ValueError):
            self.call("PreToolUse")
        self.profile["state_dir"] = str(self.base)
        with self.assertRaises(ValueError):
            self.call("PreToolUse")

    def test_state_requires_private_permissions(self):
        self.state.chmod(0o755)
        with self.assertRaises(ValueError):
            self.call("PreToolUse")

    def test_output_symlink_cannot_touch_other_session(self):
        victim = self.base / "protected-session.jsonl"
        victim.write_text("untouched")
        key = hashlib.sha256(b"isolated-eval\0eval-turn-1").hexdigest()
        (self.state / (key + ".before.json")).symlink_to(victim)
        with self.assertRaises(ValueError):
            self.call("PreToolUse")
        self.assertEqual(victim.read_text(), "untouched")

    def test_atomic_writer_rejects_hardlink(self):
        import os
        victim = self.base / "protected-session.jsonl"
        victim.write_text("untouched")
        dest = self.state / "receipt.json"
        os.link(victim, dest)
        with self.assertRaises(ValueError):
            hook.private_write(dest, {})
        self.assertEqual(victim.read_text(), "untouched")

    def test_checker_failure_visible_not_pass_or_continuation(self):
        profile = self.base / "profile.json"
        profile.write_text(json.dumps(self.profile))
        (self.root / "projectos.audit.json").write_text('{"invalid": true}')
        result = subprocess.run([sys.executable, "-B", str(fixtures.SKILL_ROOT / "scripts/projectos_hook.py"),
                                 "--profile", str(profile)], input=json.dumps(self.event), text=True, capture_output=True)
        output = json.loads(result.stdout)
        self.assertIn("unchecked", output["systemMessage"])
        self.assertNotIn("decision", output)

    def test_interrupt_does_not_create_state_or_continue(self):
        self.assertEqual(self.call("Interrupt"), {})
        self.assertEqual(list(self.state.iterdir()), [])

    def enable_lifecycle(self):
        import lifecycle_change as change
        from test_transition_audit import EXIT_TABLE
        plan=self.root/'doc/IMPLEMENTATION_PLAN.md';plan.write_text(plan.read_text()+EXIT_TABLE)
        contract=self.root/'docs/CONTRACT.md';contract.parent.mkdir()
        contract.write_text('Status: Active\nContract Version: 1\nLast Verified Against: pending implementation\n\nFrozen requirements.\n')
        (self.root/'source.py').write_text('x = 1\n');(self.root/'check.txt').write_text('bounded check passed\n')
        op=self.state/'operations';op.mkdir(mode=0o700)
        log=self.state/'trusted.jsonl';self.profile['trusted_lifecycle_log']=str(log)
        return change,contract,op,log

    def entry_call(self, change, op, log, request, call_id):
        r=change.apply(self.root,op,request);self.assertEqual(r['status'],'applied',r)
        with log.open('a') as f:f.write(json.dumps({'thread_id':self.event['session_id'],'turn_id':self.event['turn_id'],
            'call_id':call_id,'request':request,'result':r})+'\n')
        return r

    def lifecycle_request(self, op='one'):
        return dict(operation_id=op,task_ids=['T-001'],exit_ids=[],read_paths=[],decisions={},
                    edits=[dict(path='TODO.md',old='| Ready |',new='| Blocked |')])

    def test_complete_receipt_false_propagates_to_final_observe_hook(self):
        change,p,op,log=self.enable_lifecycle();self.call('PreToolUse')
        r=self.entry_call(change,op,log,self.lifecycle_request(),'a');self.call('PostToolUse')
        self.call('PreToolUse');p.write_text(p.read_text().replace('pending implementation','direct metadata edit'));self.call('PostToolUse')
        self.assertFalse(change.receipt_current(self.root,r))
        final=self.call('Stop');self.assertIn('Lifecycle entry coverage: unverified',final['systemMessage']);self.assertNotIn('decision',final)
        report=json.loads(next(self.state.glob('*.receipt.json')).read_text())['report']['lifecycle_receipt_coverage']
        self.assertEqual(report['mapped_owner_coverage'],'covered');self.assertIn('docs/CONTRACT.md',report['uncovered_related_inputs'])
        self.assertEqual(json.loads(next(self.state.glob('*.receipt.json')).read_text())['report']['status'],'unverified')

    def test_metadata_entry_and_legal_successor_are_covered_by_hook(self):
        change,p,op,log=self.enable_lifecycle();self.call('PreToolUse')
        q=self.lifecycle_request();q['verification_updates']=[{'path':'docs/CONTRACT.md','old':'pending implementation','status':'partial',
           'scope':'x only','sources':['source.py'],'evidence':['check.txt'],'reason':'bounded check'}]
        first=self.entry_call(change,op,log,q,'a');self.call('PostToolUse');self.call('PreToolUse')
        q=copy.deepcopy(q);q.update(operation_id='two',edits=[]);q['verification_updates'][0].update(old=change.header_field(p.read_text(),'Last Verified Against'),status='verified')
        last=self.entry_call(change,op,log,q,'b');self.call('PostToolUse')
        self.assertFalse(change.receipt_current(self.root,first));self.assertTrue(change.receipt_current(self.root,last))
        self.assertIn('Lifecycle entry coverage: covered',self.call('Stop')['systemMessage'])

    def test_hook_retains_observed_bypass_even_after_restoration(self):
        change,p,op,log=self.enable_lifecycle();self.call('PreToolUse');old=p.read_text()
        p.write_text(old.replace('pending implementation','uncovered'));self.call('PostToolUse');self.call('PreToolUse')
        p.write_text(old);self.call('PostToolUse')
        self.assertIn('Lifecycle entry coverage: unverified',self.call('Stop')['systemMessage'])

    def test_missing_full_preedit_hook_observation_is_unverified(self):
        change,p,op,log=self.enable_lifecycle();self.call('PreToolUse')
        next(self.state.glob('*.lifecycle.json')).unlink()
        self.assertIn('Lifecycle entry coverage: unverified',self.call('Stop')['systemMessage'])
