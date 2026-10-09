#!/usr/bin/env python3
"""Opt-in, session- or project-scoped ProjectOS hook. Writes only private state.

No hook is installed by this script. Supply --profile explicitly; stdin is the
host hook event JSON. Default mode only observes. Never edits project documents.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
import re
import stat
from pathlib import Path
import sys
import tempfile

import audit_project_docs as audit
import audit_project_transition as transition


def load(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=audit.unique_json_object)


def private_write(path, value):
    # State paths are generated digests, not host-provided path components.
    if path.is_symlink() or (path.exists() and (not path.is_file() or path.stat().st_nlink != 1)):
        raise ValueError("Adapter output aliases another file")
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".projectos-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(value, out, ensure_ascii=False, indent=2)
            out.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def extra(event, message):
    if event in {"SessionStart", "PreToolUse", "PostToolUse"}:
        return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": message}}
    return {"systemMessage": message}


@contextmanager
def turn_lock(path):
    # Separate hook processes can overlap in code mode. Keep the inode: unlinking
    # a lock after release would let waiters lock different files for one turn.
    import fcntl
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_mode & 0o077:
            raise ValueError("Adapter lock must be a private regular file without aliases")
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def run(profile, event):
    if profile.get("schema") != "projectos-hook-v1":
        raise ValueError("Unsupported profile schema")
    scope = profile.get("session_scope", "allowlist")
    if scope not in {"allowlist", "project"}:
        raise ValueError("session_scope must be allowlist or project")
    allowed = profile.get("allowed_sessions", [])
    if not isinstance(allowed, list) or any(not isinstance(x, str) or not x or x == "*" for x in allowed):
        raise ValueError("allowed_sessions must contain explicit session IDs, never a wildcard")
    excluded = profile.get("excluded_sessions", [])
    if not isinstance(excluded, list) or any(not isinstance(x, str) or not x or x == "*" for x in excluded):
        raise ValueError("excluded_sessions must contain explicit session IDs, never a wildcard")
    sid = event.get("session_id")
    if not isinstance(sid, str) or not sid.strip() or sid in excluded:
        return {}
    if scope == "allowlist" and sid not in allowed:
        return {}  # No state writes or project reads for an unlisted session.
    if scope == "project":
        if allowed:
            raise ValueError("project scope replaces allowed_sessions; omit it or use an empty list")
        if profile.get("mode", "observe") != "observe" or profile.get("authorized_write_turns", []):
            raise ValueError("project scope supports observe only, without authorized_write_turns")
    cwd_value = event.get("cwd")
    if not isinstance(cwd_value, str) or not cwd_value or not Path(cwd_value).is_absolute():
        raise ValueError("Host cwd must be a nonempty absolute path")
    root = Path(profile["project_root"])
    if not root.is_absolute() or root.is_symlink():
        raise ValueError("Use an absolute, non-symlink project root")
    root = root.resolve(strict=True)
    cwd = Path(cwd_value).resolve(strict=True)
    if not cwd.is_relative_to(root):
        return {}
    if scope == "project":
        # Resolve symlinks first, then stop at nested repositories/worktrees.
        # A plain subdirectory belongs to this root; a .git boundary does not.
        current = cwd
        while current != root:
            if (current / ".git").exists() or (current / ".git").is_symlink():
                return {}
            current = current.parent
    mode = profile.get("mode", "observe")
    if mode not in {"observe", "bounded"}:
        raise ValueError("mode must be observe or bounded")
    name = event.get("hook_event_name")
    if name == "SessionStart":
        return extra(name, "ProjectOS: use this project's effective entrypoint and relevant current owners. "
                     "Within authorized work, retire replaced facts and preserve unfinished acceptance. "
                     "Read-only requests do not claim tasks or write back. No new authorization is supplied by this hook.")
    if name not in {"PreToolUse", "PostToolUse", "Stop"}:
        return {}
    turn = event.get("turn_id")
    if not isinstance(turn, str) or not turn:
        return extra(name, "ProjectOS unchecked: host did not supply a turn identity; no baseline or continuation created.")
    state = Path(profile["state_dir"])
    if not state.is_absolute() or state.is_symlink():
        raise ValueError("Use an absolute, non-symlink private state directory")
    # Require an existing task-owned directory. Never create host/global/session directories.
    state = state.resolve(strict=True)
    if state.is_relative_to(root) or root.is_relative_to(state):
        raise ValueError("Adapter state must be outside and not contain the project")
    if not state.is_dir() or state.stat().st_mode & 0o077:
        raise ValueError("Adapter state must be a private (0700) directory")
    key = hashlib.sha256((sid + "\0" + turn).encode()).hexdigest()
    with turn_lock(state / (key + ".lock")):
        return run_turn(profile, event, root, state, key, name, turn, mode)


def lifecycle_observation(profile, event, root, state, key, name):
    """Trusted opt-in event observations; never synthesize a post-edit baseline."""
    import lifecycle_change
    log = Path(profile['trusted_lifecycle_log'])
    observation = state / (key + '.lifecycle.json')
    if (not log.is_absolute() or log.is_symlink() or log.parent != state
            or observation.is_symlink()):
        raise ValueError('Lifecycle log/observation must be in private adapter state')
    calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    if any(c.get('thread_id') != event['session_id'] for c in calls):
        raise ValueError('Lifecycle receipt belongs to another session')
    calls = [c for c in calls if c.get('turn_id') == event['turn_id']]
    if observation.exists():
        recorded = load(observation)
    elif name == 'PreToolUse':
        recorded = {'baseline': lifecycle_change.capture_receipt_state(root, config_arg=profile.get('config')),
                    'failures': []}
    else:
        return {'status': 'unverified', 'uncovered_owners': [], 'errors': ['full pre-edit receipt observation missing']}
    current, coverage = lifecycle_change.observe_receipts(
        root, recorded['baseline'], calls, recorded['failures'], profile.get('config'))
    recorded.update(failures=coverage['historical_unverified_boundaries'], current=current, coverage=coverage)
    private_write(observation, recorded)
    return coverage


def run_turn(profile, event, root, state, key, name, turn, mode):
    # Baseline, taint and continuation receipt must be inspected and written
    # under one per-turn lock, including capture and compare.
    baseline = state / (key + ".before.json")
    receipt = state / (key + ".receipt.json")
    tainted = state / (key + ".tainted.json")
    if any(p.is_symlink() for p in (baseline, receipt, tainted)):
        raise ValueError("Adapter state entry is a symlink")
    if tainted.exists():
        return extra(name, "ProjectOS unchecked: this turn missed its pre-edit baseline; later events cannot recreate it. No automatic continuation.")
    if name == "PreToolUse":
        if not baseline.exists():
            private_write(baseline, transition.capture(root, profile.get("config")))
        if profile.get('trusted_lifecycle_log'):
            lifecycle_observation(profile, event, root, state, key, name)
        return {}
    if name == "PostToolUse":
        # Tools have already run; no baseline may be manufactured here.
        if not baseline.exists():
            private_write(tainted, {"status": "unchecked", "reason": "post-tool event preceded baseline"})
            return extra(name, "ProjectOS unchecked: first pre-tool baseline is missing; post-tool state cannot replace it.")
        if profile.get('trusted_lifecycle_log'):
            lifecycle_observation(profile, event, root, state, key, name)
        return {}
    if not baseline.exists():
        return extra(name, "ProjectOS unchecked: no pre-edit baseline in this turn; no automatic continuation.")
    before = transition.load_snapshot(baseline)
    after = transition.capture(root, profile.get("config"))
    report = transition.compare(before, after)
    if profile.get('trusted_lifecycle_log'):
        report['lifecycle_receipt_coverage'] = lifecycle_observation(profile, event, root, state, key, name)
        report['mapped_transition_status'] = report['status']
        if report['lifecycle_receipt_coverage']['status'] != 'covered':
            report['status'] = 'unverified'
    previous = load(receipt) if receipt.exists() else {}
    blocked = bool(previous.get("continued", False))
    # Bounded continuation is an extra opt-in for an exact authorized turn.
    # permission_mode is tool permission, NOT scope authorization/read-only intent.
    turns = profile.get("authorized_write_turns", [])
    if not isinstance(turns, list) or any(not isinstance(x, str) or x == "*" for x in turns):
        raise ValueError("authorized_write_turns must be explicit turn IDs")
    def signature(item):
        message = re.sub(r"first at line \d+", "first occurrence", item["message"])
        return item["code"], item["path"], message

    preexisting = {signature(x) for x in transition.compare(before, before)["findings"]}
    deterministic = any(x["severity"] == "ERROR" and signature(x) not in preexisting
                        for x in report["findings"])
    continue_once = (mode == "bounded" and turn in turns and deterministic
                     and bool(report["changed_files"]) and not blocked
                     and not event.get("stop_hook_active", False)
                     and event.get("permission_mode") != "plan")
    private_write(receipt, {"continued": blocked or continue_once, "report": report})
    codes = sorted({x["code"] for x in report["findings"]})
    message = (f"ProjectOS transition {report['status']}; changed owners: {len(report['changed_files'])}; "
               f"findings: {', '.join(codes) or 'none'}. Receipt: {receipt}. "
               "This does not verify implementation, approvals or artifact contents. "
               "If implementation changed without owner changes, inspect whether writeback is needed.")
    if 'lifecycle_receipt_coverage' in report:
        c = report['lifecycle_receipt_coverage']
        message += (f" Lifecycle entry coverage: {c['status']}; uncovered owners: {c['uncovered_owners']}; "
                    f"related inputs: {c.get('uncovered_related_inputs', [])}; errors: {c['errors']}. "
                    "Observe mode does not undo writes or block all paths.")
    if continue_once:
        return {"decision": "block", "reason": message +
                " Review and repair only necessary synchronization already authorized for this turn. "
                "Do not execute backlog tasks, lower acceptance or override a read-only instruction. "
                "If not repairable within scope, report the unresolved finding and stop."}
    return {"systemMessage": message}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", type=Path, required=True)
    args = ap.parse_args()
    try:
        event = json.load(sys.stdin, object_pairs_hook=audit.unique_json_object)
        result = run(load(args.profile), event)
    except Exception as exc:
        # Checker failure must be visible, but must not become a continuation loop.
        result = {"systemMessage": f"ProjectOS unchecked: {type(exc).__name__}: {exc}. No automatic continuation."}
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
