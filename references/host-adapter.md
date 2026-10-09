# Optional Codex adapter

This adapter is opt-in and does not install, alter or resume any session. Keep core adoption usable without it. Use `scripts/projectos_hook.py --profile /absolute/private/profile.json` as a command hook only after explicit host integration. Never install it globally while preserving existing sessions is required.

Official contract checked 2026-10-02: https://learn.chatgpt.com/docs/hooks . Local capability discovery is not a runtime delivery test. SessionStart supports startup/resume/compact; PreToolUse can observe the first tool before edits; PostToolUse is too late to create a missing before-state. Stop continuation is subject to stop_hook_active and must remain bounded. Background hook completion does not start an idle conversation. Recheck host event schema/trust before deployment.

## Profile and isolation

Choose a session scope explicitly when preparing an integration:

- `session_scope: "allowlist"` (the backwards-compatible default): only the exact `allowed_sessions` IDs are admitted. Use for isolated trials or bounded continuation.
- `session_scope: "project"`: automatically admit current and future sessions whose resolved cwd is in the configured project. Supports **observe only**, with no write-turn grants. No session registration or profile mutation is needed for a new session. Omit `allowed_sessions` or leave it empty; a nonempty list is rejected to avoid implying it restricts project enrollment.
- In either scope, optional `excluded_sessions` lists exact session IDs to leave untouched, including protected existing conversations. Exclusions take precedence. Wildcards are not supported.

Project scope covers the root and its ordinary subdirectories. A nested `.git` file/directory is a separate repository/worktree boundary and is excluded, as are sibling/external worktrees and symlinks resolving outside the root. Give each worktree its own root, profile and private state directory, and verify where that host actually loads the Hook definitions; some hosts redirect linked-worktree Hook sources to the primary checkout (see below). Plain nested directories without a Git boundary remain part of the configured project. This is a cwd-based routing policy, not proof of which files a tool will edit, and does not coordinate simultaneous project writers.

Example allowlist profile (replace paths and exact IDs only in a new, task-owned test host):

```json
{
  "schema": "projectos-hook-v1",
  "session_scope": "allowlist",
  "project_root": "/isolated/project",
  "state_dir": "/isolated/private-adapter-state",
  "allowed_sessions": ["new-isolated-evaluation-session"],
  "mode": "observe",
  "authorized_write_turns": []
}
```

For one-time project enrollment, use this profile instead (the paths are illustrative):

```json
{
  "schema": "projectos-hook-v1",
  "session_scope": "project",
  "project_root": "/absolute/project",
  "state_dir": "/absolute/private-projectos-state",
  "mode": "observe",
  "authorized_write_turns": [],
  "excluded_sessions": []
}
```

If needed, the existing `config` field points to the project's audit mapping. A missing host session or turn identity does not create shared state; project enrollment does not remove identity requirements.

Create state_dir as a private 0700 directory outside the project and outside the host's real sessions/index/config directories. It holds only this adapter's content snapshots and receipts. Snapshots contain selected owner text; preserve or clean them only under the task's retention authority. The adapter requires the directory to exist and does not create a global storage location.

An event from an excluded session, or an unlisted session in allowlist scope, returns an empty object before reading project files or writing state. A cwd outside the mapped project is ignored; missing or relative cwd is rejected before project reads. Paths are resolved; no wildcard session IDs or turn authorization is supported. Turn state is separated by a digest of session ID and turn ID, with atomic private writes and symlink/hard-link rejection for output files. Never infer user scope from the host permission_mode.

Overlapping events for one turn serialize baseline capture, taint and continuation receipt under a private per-turn file lock. Keep its lock file until authorized state cleanup; deleting it while another hook waits could split the lock. This adapter requires POSIX `flock` support in its private state directory. Unsupported locking is an unchecked integration failure. The lock protects adapter bookkeeping only; it does not lock project files or coordinate other project writers.

Register SessionStart, PreToolUse, PostToolUse and Stop to the same command. Use JSON hookSpecificOutput for supported additionalContext and systemMessage for nonblocking Stop feedback. Do not use blocking PostToolUse: in code mode it may reject a nested tool result after the mutation already happened. The adapter uses only nonblocking PostToolUse feedback.

### Check the actual host first

Before configuring a project or launching a second host, identify the user's actual client, runtime version/build, connection transport, executor, effective cwd/project root, configuration layers and inference route. Query its hook-discovery interface at that exact root. An empty list is **not** proof that command Hooks are unsupported: inspect project trust, root detection, file format, effective layers and loader warnings first. Do not switch models to diagnose configuration or transport failures.

On the verified Codex 0.161.0 desktop Unix endpoint, the control protocol is WebSocket over the Unix socket; a raw JSON-lines client hangs. Standalone `app-server --listen stdio://` uses JSON lines and is a different transport. Do not start or restart a shared server just to probe it. In this environment, project Hooks in `.codex/hooks.json` loaded only after the exact resolved project root was trusted; trusting a parent directory did not suffice. These are observed version-specific conditions, not universal assumptions about other clients. Project trust and exact command/hash trust remain separate.

**Linked worktrees need a source-path check.** In Codex 0.161.0, a linked worktree keeps its ordinary project configuration but loads project Hook definitions from the matching primary-checkout `.codex` directory. The loader replaces the worktree's inline `[hooks]` declarations and redirects `hooks.json` discovery; changing JSON versus TOML inside the worktree cannot repair that source mismatch. This was reproduced in an isolated real Git worktree and matches the [version-pinned loader implementation](https://github.com/openai/codex/blob/979011409de0a60b52f179721948e65531d26144/codex-rs/config/src/loader/mod.rs#L1782). Check `hooks/list.sourcePath`, not just `config/read`'s project-layer path.

A primary-checkout source can point to a profile restricted to the requested worktree. The qualified adapter returns empty output and writes no state outside that root, but the shared source handlers can still be discovered/invoked in the primary checkout and sibling worktrees. Do not silently write into a protected primary checkout, use a global dispatch Hook, rewrite Git metadata or expand trust to bypass this boundary. Prepare the exact primary-source diff and obtain any required scope exception. If that scope is unavailable, report the project as blocked on the verified loader boundary; the core Skill remains usable without Hooks. Ordinary checkouts and worktrees with a supported source are distinct applicability cases.

If actual-host discovery or delivery fails, record the failing layer and stop dependent enrollment. Enter a separately scoped host-adaptation investigation. A standalone host with a different request path cannot qualify the daily desktop environment. Never repair credentials, broaden permissions or alter shared services merely to obtain a passing test.

### Reusable host qualification

Full developer qualification belongs to a release and a defined environment, not to every project's first setup. The shipped [scoped qualification receipt](host-qualification.json) records the observed Codex 0.161.0 desktop path, tested cases and explicit limits; match its conditions before reuse. Keep a qualification receipt with the adapter revision/content hash, client/runtime build, transport and executor, relevant effective configuration, project-root/trust rules, handler definition, profile schema/scope/mode, tested cases and raw event/state evidence. Separate authenticated inference from controlled transport and direct event simulation. Record failures and unsupported coverage explicitly.

For project-observe qualification, use two fresh sessions with an unchanged profile, separate per-session state, actual SessionStart/PreToolUse/PostToolUse/Stop delivery, a before/after fixture-owner change, an excluded session and an out-of-project case. Preserve event-level allowlist/bounded and path-boundary regression coverage separately. Compaction/recovery, interrupts and error handling need their own evidence for any claim about those behaviors. Bounded continuation is not enabled or qualified by project-observe enrollment.

A receipt is reusable only while the relevant adapter implementation, host/runtime, request/execution route, configuration and scope semantics still match. Project-specific roots and command paths require fresh discovery and exact trust; owner mappings require inspection. Changes invalidate affected coverage, not unrelated evidence. A different host/version/path or an unexplained discovery mismatch goes back to adaptation/qualification. Do not call package tests or a controlled server a real authenticated-model qualification.

### One-time project setup

After the user requests enrollment:

1. Check the actual host above and select an applicable qualification receipt. Reuse it; do not rebuild a model test environment for each project.
2. Inspect the project's current owners, pending edits and operation journals. Preserve unfinished work and any protected existing session IDs. Prepare a private `session_scope: "project"`, `mode: "observe"` profile with no write-turn grants and explicit exclusions. Use the project's existing audit mapping.
3. Check the source path the host will actually load, including primary-checkout redirection and its authorization boundary. Merge four synchronous project command handlers for SessionStart, PreToolUse, PostToolUse and Stop, preserving unrelated handlers. Run the installed Python interpreter and `scripts/projectos_hook.py --profile /absolute/private/profile.json`, with shell-quoted actual paths. Keep machine-specific paths, profile and state local. Do not register a global handler or make baseline/Stop handlers asynchronous.
4. Review the effective definitions through the host's supported interface (`/hooks` in the CLI). Trust only the exact project path and reviewed command hashes as needed. Re-list and require four enabled, trusted handlers with unchanged hashes. Project trust alone is insufficient; a file on disk is not proof of loading.
5. Run one small fresh-session smoke check on that same working host, normally a read-only tool call. Require actual event completions, a pre-tool baseline and a Stop receipt with matching session/turn IDs. Inspect receipt findings and mapping coverage; a delivered structural report may still be partial. A second project session or the full developer suite is needed only for a changed assumption or unresolved failure, not by default.
6. Record implementation/package status, applicable host qualification, project configuration/trust, actual smoke result and remaining limits separately. Explain exclusions and how to disable the project's handlers. If blocked, keep a concrete blocked status and the raw failure; do not say enrollment is usable.

Once these checks pass, future sessions under the configured root need no session-ID registration or repeated enrollment request. Existing sessions may match after configuration reload, so exclusions must be in place before activation. Disable the project's handlers through the host to stop observation, or explicitly return to allowlist scope. Preserve receipts when disabling. A changed definition may require renewed exact trust.

Interrupted sessions can request setup without discarding their work. There is no retroactive coverage: never reconstruct missing pre-edit baselines. If a running client cannot reload configuration, continue from preserved project state in a new session. Do not resume a paused Goal or authorize queued scientific work as part of Hook setup.

For Codex app-server versions with a verified write interface, review `hooks/list` and trust only its returned exact `key` and `currentHash` using `config/batchWrite` (`hooks.state`, per-key `trusted_hash`, upsert, reloadUserConfig). Preserve all unrelated state and re-list hashes/status before opening a test thread. The same principle applies to exact project trust. A CLI bypass flag is not proof that app-server thread trust changed. In particular, the 0.159.2 standalone host did not forward `--dangerously-bypass-hook-trust` to thread configuration.

## Event behavior

- SessionStart: short routing/context reminder; does not read all history or claim work.
- First PreToolUse per turn: capture relevant owners before tools run. Later calls reuse this baseline, not a post-edit replacement. This also captures before a read-only first tool; no project files are modified.
- PostToolUse: report missing baseline if the host missed pre-tool delivery. A missing baseline poisons that turn persistently: later pre-tool or Stop events cannot reconstruct it or report a pass. It does not pretend to infer every edited path from shell command text.
- Stop: compare actual owners to that baseline and save a report. No owner changes does not prove code and docs agree: the reminder asks for a scoped semantic check when implementation changed. The report declares unsupported coverage.

Default observe mode never creates a continuation. Bounded mode additionally requires an exact authorized_write_turns entry, actual changed owner files and newly introduced deterministic structural errors. Pre-existing findings remain in the receipt but do not force unrelated repair. It permits at most one continuation per turn receipt, respects stop_hook_active and plan mode, and never continues solely for warning/no-baseline/checker failure. Read-only turns must never appear in authorized_write_turns; this adapter does not attempt to parse user authority from arbitrary transcript prose. The host/caller must supply that explicit contract. Its reason confines repair to already authorized synchronization and asks for an honest unresolved report when repair is not allowed.

The adapter is a reminder/checker, not an autonomous task runner. It cannot wake a new turn on GPU completion, verify scientific acceptance, prove that all code edits require writeback, or safely coordinate arbitrary competing writers. Continue to inspect conflicts and use the project's established ownership rules.

## Acceptance and delivery claims

Run relevant event-level regressions and package validation when changing the adapter. Use the reusable host qualification above for actual runtime acceptance. Ordinary project enrollment uses an applicable receipt plus its local smoke check. Keep the exact profile, client version, event traces and owner diffs as evidence; direct JSON simulation alone cannot establish host or model behavior.

A formal release identifies shipped bytes and their tested support boundary. Installation, release publication, host qualification and individual project enrollment are separate facts. Report each explicitly. A published package must not imply that every desktop, remote or cloud executor has been tested. For project entrypoints, static discovery cannot prove actual model ingestion; inspect overrides, nested/worktree scopes and size limits without replacing existing documents wholesale.

## Optional explicit change receipts

A host may expose `projectos.change` using `scripts/lifecycle_change.py` without enabling a Hook. Keep the entry's operation journal and real call/return log outside model-writable project paths. The host binds the project itself, accepts only the documented replacements, and never wraps arbitrary commands. It must retain ordinary direct tools so this mode is not misrepresented as enforced editing.

For the Hook, `trusted_lifecycle_log` can name a host-owned JSONL file directly under `state_dir`. Each record contains call_id, thread_id, request and the actual entry result. The Hook validates session, candidate binding, request digest, five execution steps and before/after owner continuity at Stop. Do not point this at model-written logs. This opt-in check reports missing/stale/bypassed coverage; observe mode does not block or undo writes. Independent tool-boundary observation is still needed to detect intermediate bypass even when final bytes were restored. Unknown paths, free-text semantics and authority remain outside this structural guarantee.

The optional trusted lifecycle integration observes related read inputs/configuration as well as mapped writes. It shares complete receipt validation with the entry, preserves chronological before-state continuity and retains unverified tool boundaries. A valid later operation may supersede a prior receipt; a latest receipt alone cannot hide an earlier uncovered edit. Missing full observation is unverified. Observe mode still neither repairs nor intercepts ordinary edits.
