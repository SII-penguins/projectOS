# Optional Codex adapter

This adapter is opt-in and does not install, alter or resume any session. Keep core adoption usable without it. Use `scripts/projectos_hook.py --profile /absolute/private/profile.json` as a command hook only after explicit host integration. Never install it globally while preserving existing sessions is required.

Official contract checked 2026-10-02: https://learn.chatgpt.com/docs/hooks . Local capability discovery is not a runtime delivery test. SessionStart supports startup/resume/compact; PreToolUse can observe the first tool before edits; PostToolUse is too late to create a missing before-state. Stop continuation is subject to stop_hook_active and must remain bounded. Background hook completion does not start an idle conversation. Recheck host event schema/trust before deployment.

## Profile and isolation

Example profile shape (replace paths and exact IDs only in a new, task-owned test host):

```json
{
  "schema": "projectos-hook-v1",
  "project_root": "/isolated/project",
  "state_dir": "/isolated/private-adapter-state",
  "allowed_sessions": ["new-isolated-evaluation-session"],
  "mode": "observe",
  "authorized_write_turns": []
}
```

Create state_dir as a private 0700 directory outside the project and outside the host's real sessions/index/config directories. It holds only this adapter's content snapshots and receipts. Snapshots contain selected owner text; preserve or clean them only under the task's retention authority. The adapter requires the directory to exist and does not create a global storage location.

An event from an unlisted session returns an empty object before reading project files or writing state. A cwd outside the mapped project is ignored; missing or relative cwd is rejected before project reads. Paths are resolved; no wildcard session IDs or turn authorization is supported. Turn state is separated by a digest of session ID and turn ID, with atomic private writes and symlink/hard-link rejection for output files. Never infer user scope from the host permission_mode.

Overlapping events for one turn serialize baseline capture, taint and continuation receipt under a private per-turn file lock. Keep its lock file until authorized state cleanup; deleting it while another hook waits could split the lock. This adapter requires POSIX `flock` support in its private state directory. Unsupported locking is an unchecked integration failure. The lock protects adapter bookkeeping only; it does not lock project files or coordinate other project writers.

Register SessionStart, PreToolUse, PostToolUse and Stop to the same command. Use JSON hookSpecificOutput for supported additionalContext and systemMessage for nonblocking Stop feedback. Do not use blocking PostToolUse: in code mode it may reject a nested tool result after the mutation already happened. The adapter uses only nonblocking PostToolUse feedback.

On Codex 0.159.2 standalone app-server, the CLI `--dangerously-bypass-hook-trust` flag is not forwarded to the thread configuration. Project trust is also distinct from hook trust. In a private, explicitly authorized evaluation home, inspect `hooks/list`, review each command, and trust only its returned exact `key` and `currentHash` through `config/batchWrite` (`hooks.state`, per-key `trusted_hash`, upsert, reloadUserConfig). Re-list and require unchanged hashes with `trustStatus: trusted` before starting a new thread. This changes only that private home's config. Do not use a managed/global hook or broaden trust to work around this boundary. Other client versions need their own verified integration path.

## Event behavior

- SessionStart: short routing/context reminder; does not read all history or claim work.
- First PreToolUse per turn: capture relevant owners before tools run. Later calls reuse this baseline, not a post-edit replacement. This also captures before a read-only first tool; no project files are modified.
- PostToolUse: report missing baseline if the host missed pre-tool delivery. A missing baseline poisons that turn persistently: later pre-tool or Stop events cannot reconstruct it or report a pass. It does not pretend to infer every edited path from shell command text.
- Stop: compare actual owners to that baseline and save a report. No owner changes does not prove code and docs agree: the reminder asks for a scoped semantic check when implementation changed. The report declares unsupported coverage.

Default observe mode never creates a continuation. Bounded mode additionally requires an exact authorized_write_turns entry, actual changed owner files and newly introduced deterministic structural errors. Pre-existing findings remain in the receipt but do not force unrelated repair. It permits at most one continuation per turn receipt, respects stop_hook_active and plan mode, and never continues solely for warning/no-baseline/checker failure. Read-only turns must never appear in authorized_write_turns; this adapter does not attempt to parse user authority from arbitrary transcript prose. The host/caller must supply that explicit contract. Its reason confines repair to already authorized synchronization and asks for an honest unresolved report when repair is not allowed.

The adapter is a reminder/checker, not an autonomous task runner. It cannot wake a new turn on GPU completion, verify scientific acceptance, prove that all code edits require writeback, or safely coordinate arbitrary competing writers. Continue to inspect conflicts and use the project's established ownership rules.

## Host acceptance before deployment

Run event-level regressions first. In a newly authorized isolated host, verify actual SessionStart delivery, pre-edit baseline capture, after-edit Stop receipt, compaction/recovery reminder, user interrupt, read-only scope, errors, and bounded continuation once. Confirm no events/state updates for a separate unlisted session. Do not claim host/model behavior from direct JSON event simulation. Keep the exact profile, client version, event traces and owner diffs as evidence.

For existing projects, prepare minimal entrypoint/config diffs and verify effective instruction discovery (overrides, nested scopes, worktree and size limits). A static file check cannot prove actual model ingestion. Never overwrite an old AGENTS.md with a whole template or use a live long-running conversation as the first experiment.

## Optional explicit change receipts

A host may expose `projectos.change` using `scripts/lifecycle_change.py` without enabling a Hook. Keep the entry's operation journal and real call/return log outside model-writable project paths. The host binds the project itself, accepts only the documented replacements, and never wraps arbitrary commands. It must retain ordinary direct tools so this mode is not misrepresented as enforced editing.

For the Hook, `trusted_lifecycle_log` can name a host-owned JSONL file directly under `state_dir`. Each record contains call_id, thread_id, request and the actual entry result. The Hook validates session, candidate binding, request digest, five execution steps and before/after owner continuity at Stop. Do not point this at model-written logs. This opt-in check reports missing/stale/bypassed coverage; observe mode does not block or undo writes. Independent tool-boundary observation is still needed to detect intermediate bypass even when final bytes were restored. Unknown paths, free-text semantics and authority remain outside this structural guarantee.

The optional trusted lifecycle integration observes related read inputs/configuration as well as mapped writes. It shares complete receipt validation with the entry, preserves chronological before-state continuity and retains unverified tool boundaries. A valid later operation may supersede a prior receipt; a latest receipt alone cannot hide an earlier uncovered edit. Missing full observation is unverified. Observe mode still neither repairs nor intercepts ordinary edits.
