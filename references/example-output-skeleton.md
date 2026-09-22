# Minimal Document Examples

Adapt only the relevant examples. Replace placeholders from inspected facts, user decisions or explicitly identified assumptions. Do not generate every example or mark unknown results as passed. Metadata dates describe actual reconciliation, not when an old claim was merely copied.

For a small project these responsibilities can be sections of one plan/state file. The separated examples show the auditor's supported syntax.

To audit a combined file, map each role to its heading using `references/audit-format.md`. Keep active and terminal rows in different sections; do not map both roles to the entire file. Retain source/decision references when adopting a contract or correcting evidence, as described in `references/lifecycle-transitions.md`.

## Agent routing

~~~markdown
# AGENTS.md
Status: Active
Canonical For: local operating constraints and task-specific document routing
Last Reconciled: <date>
Freshness Rule: Update when commands, contracts or document ownership changes.
Archive Rule: Preserve superseded instructions in version control.

For resumed project work, use PROGRESS.md for live state and TODO.md for the queue.
For roadmap decisions, use doc/IMPLEMENTATION_PLAN.md.
Read domain contracts only when the task touches their interfaces.
Keep only project-specific commands and constraints here.

When a requested change alters a task outcome, blocker/next action, accepted interface
or evidence status, update the corresponding existing owner and affected references.
Leave unchanged facts alone; an isolated edit does not require new project documents.
~~~

## Live state

~~~markdown
# PROGRESS.md
Status: Active
Canonical For: current phase, blocker, evidence boundary and resume point
Last Reconciled: <date>
As Of: <date>
Freshness Rule: Reconcile when phase, blocker, artifacts or next action changes.
Archive Rule: Promote durable outcomes to the roadmap or ledger before compacting.

Current Phase: S1
Next Task: T-001
Next Action: T-001 — <next authorized action>
Blocker: <observed blocker or none>
Evidence boundary: <what is verified and what is not>
~~~

## Active work

~~~markdown
# TODO.md
Status: Active
Canonical For: active task status, ownership, dependencies and acceptance
Last Reconciled: <date>
Freshness Rule: Update on task state, dependency or acceptance changes.
Archive Rule: Move terminal outcomes to doc/archive/TASKS.md; keep blocked/review work here.

| ID | Status | Owner | Dependencies | Next Action | Acceptance Gate | Evidence | Last Touched |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-001 | Ready | <owner> | None | <action> | <observable criterion> | Pending | <date> |
~~~

## Roadmap

~~~markdown
# IMPLEMENTATION_PLAN.md
Status: Active
Canonical For: stage meaning, transitions and exit criteria
Last Reconciled: <date>
Freshness Rule: Reconcile when stage scope or exit criteria changes.
Archive Rule: Retain completed phase outcome, evidence and meaning.
Plan Version: 1

| Stage | Goal | Entry | Exit | Status |
| --- | --- | --- | --- | --- |
| S1 | <goal> | <prerequisite> | <evidence needed> | Active |
~~~

## Terminal record

~~~markdown
# TASKS.md
Status: Archived
Canonical For: terminal task outcomes and successor evidence
Last Reconciled: <date>
Freshness Rule: Update when a terminal outcome is recorded or corrected.
Archive Rule: Keep evidence and successor links accessible.

| ID | Final Status | Closed On | Evidence / Decision | Outcome |
| --- | --- | --- | --- | --- |
~~~

Add rows only for actual terminal work. A Done row needs acceptance evidence; a Cancelled row needs its cancellation decision and successor impact. A blocked task does not belong here.

If `T-001` later needs corrective work, retain its archived outcome and use a new active attempt such as `T-001-R2`, with `Reopens: T-001` or a related-history link. Do not treat that history link as a prerequisite unless successful prior work is actually required.

## Optional run ledger

~~~markdown
# RUN_REGISTRY.md
Status: Active
Canonical For: factual run history, artifacts and trust classification
Last Reconciled: <date>
Freshness Rule: Update on run outcome or trust changes.
Archive Rule: Preserve failures and corrections; shard behind a stable index if needed.

| ID | Commit / Config | Output | Outcome | Trust | Claim eligibility |
| --- | --- | --- | --- | --- | --- |
~~~

Do not add placeholder run rows. Describe trust levels in project terms; a successful parser is not sufficient proof for every downstream claim.

For a domain contract, state accepted scope/interfaces, version or verification reference, and update conditions. For a real diagnostic or lesson, preserve observations, correction and applicability. Use `references/team-blueprint.md` if a collaboration contract is needed; do not copy an assumed team roster.
