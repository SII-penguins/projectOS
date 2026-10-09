# Explicit lifecycle changes

Use `projectos.change` if the host exposes this opt-in tool. Ordinary project reads, code changes and verification use the normal tools within the user's scope. Submit governed document changes through this entry before editing them. It does not authorize the task or install a Hook.

The tool accepts one object (the six original fields are required; `verification_updates` is optional):

```json
{
  "operation_id": "record-blocker-1",
  "task_ids": ["T-001"],
  "exit_ids": [],
  "read_paths": ["receipts/latest.json"],
  "decisions": {},
  "edits": [{"path": "TODO.md", "old": "| T-001 | Ready |", "new": "| T-001 | Blocked |"}]
}
```

- `operation_id`: a new 1–80 character letter/digit/underscore/hyphen ID. Resend the **same ID and exact object** only to resume/retrieve that operation. A new intended change needs a new ID.
- `task_ids`, `exit_ids`: only the affected identities, including new rows. Unlisted rows are preserved byte-for-byte. These lists declare scope; they are not proof of authorization.
- `read_paths`: additional relevant relative inputs (contracts, source or receipts) that must not drift. Mapped owners/config and discovered stable documents are read automatically. Reads are not write permission.
- `edits`: ordered exact replacements. `old` must appear exactly once in the current file after preceding replacements. Use enough surrounding text to avoid ambiguity. Empty `old` is allowed only for a new file; no deletions, shell or arbitrary code. Ordinary replacement writes are limited to Markdown files for existing mapped progress/task/plan/run/archive owners and diagnostic Markdown under `doc/diagnostics` or `docs/diagnostics` (directory must exist). Contracts, code, config and files shared with a discovered frozen role are outside ordinary replacement scope, even if a mapping also labels them writable. The narrow verification operation below is the only exception for an existing contract provenance field. Section-mapped owner writes are currently unsupported and rejected rather than granting the whole file.
- `decisions`: affected task/exit IDs (or a retained verification-owner path) mapped to actual rationale/authority/evidence references when changing acceptance, dependencies or exit disposition. These statements require independent review. Never invent permission to satisfy a check. Existing exit IDs/requirements cannot be replaced through this entry. Add a separate obligation when appropriate; preserve old unfinished requirements and their active carriers.

## Existing verification provenance

`Last Verified Against` records what implementation/evidence the accepted rules were checked against. The accepted requirement body and `Contract Version` have separate meanings and remain frozen. An operational/lifecycle receipt does not verify the implementation. Before writing a task, stage or exit completion, inspect the existing applicable verification owner and necessary summaries against actual execution. Preserve partial/unverified scope; a passed smoke check is not full contract acceptance.

If real, applicable verification changes the existing Active contract's provenance, include this optional operation **in the same request as the related completion edits**:

```json
"verification_updates": [{
  "path": "docs/CONTRACT.md",
  "old": "the exact current Last Verified Against value",
  "status": "partial",
  "scope": "the bounded behavior actually checked; remaining behavior unverified",
  "sources": ["src/example.py"],
  "evidence": ["receipts/focused-check.txt"],
  "reason": "why the observed verification applies to this owner"
}]
```

Use real source/evidence paths, after the actual checks. Preserve valid existing evidence; if the current check has only stdout, save a truthful bounded result with the actual command/scope/outcome through ordinary tools before this operation. Do not invent a test report or edit the old raw receipt. `status` is `verified` **within the stated scope**, `partial`, or `unverified`; verified/partial require nonempty source and evidence references. Unverified may have none. The entry binds those exact current file hashes into the existing field; it does not run tests or validate their authenticity/applicability. Review the true call/return and implementation evidence separately.

Only one existing, unambiguous `Last Verified Against` header value in an Active mapped/conventional contract is writable by this operation. All other bytes, including requirements, status, version and dates, are unchanged. Do not mechanically replace a pending word, delete conflicting fields, mark a live contract historical, or refresh dates to pass a check. Historical contracts and unsupported/section-based headers are not writable. No new ledger or contract format is required.

For an unrelated contract, unchanged valid provenance, or a fact that must remain unverified, leave its bytes unchanged and put the concrete disposition reason in `decisions["path/to/contract.md"]`. A supported completion transition requires an explicit update or retention reason for existing Active verification owners. This records the decision for review; a rationale alone never proves that keeping contradictory facts is correct. Do not expand maintenance to unrelated requirements. `edits` may be empty for a standalone necessary provenance operation.

Combine related owner edits into one request so projected task/exit references are checked together. Preserve unrelated task rows and existing archive rows. The current Next Action must retain actual authorization dependencies. The entry cannot understand free text or verify research receipts.

For local CLI use, create a task-owned 0700 state directory, save the request JSON, then run:

```sh
python -B <skill>/scripts/lifecycle_change.py <project-root> --state <private-state> --request <request.json>
```

The opt-in host owns its state outside the writable project and records real calls/returns. A local CLI receipt or an editable JSON file alone has no trusted-origin guarantee. An independent observer must check actual invocation and bytes; a current valid receipt cannot excuse earlier bypasses. No-Hook mode does not block direct edits. The private Hook observes known tool paths only; its reminders are not universal enforcement.

`applied` means the program completed capture, projected checks, drift guard, writes and actual comparison. It is **not semantic acceptance**. Findings, gaps and unchecked fields remain in the receipt. `rejected` means preflight did not write project files. `incomplete` means a prepared or older operation exists and real state must be reconciled; retain the journal and actual files. Resume the same request after inspecting the reported state. The entry skips files already at their recorded result and rejects unexpected bytes. It never rolls the whole workspace back or duplicates a finished archive append.

A cooperative lock serializes this entry. Each file replacement is atomic, the set of files is not. Input versions are checked during capture, before writes and after completion; external writers ignoring the lock can still race between a check and replacement. Coordinate concurrent ownership; this is not a database transaction. Version/root mismatch refuses recovery; preserve the journal and reconcile explicitly. A later edit makes a receipt stale for those inputs. Complete observation uses the same full content/step validator as `receipt_current`, including related reads and configuration, in addition to mapped-owner write coverage. Valid successive entry operations can supersede earlier outputs only with matching before-state; earlier observed uncovered changes remain unverified even after restoration or a later receipt. Missing/unsupported observation is unverified. Receipt hashes bind bytes and code, not authority or scientific validity.
