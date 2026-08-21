# ProjectOS Lifecycle Protocol

Use this protocol whenever an existing project is resumed, reconciled, cleaned, or closed out. It supplements canonical ownership: ownership says **where a fact belongs**; lifecycle says **when it enters, changes, leaves, or remains historical**.

## 1. Information States

Classify suspect information before editing it:

- `Current`: verified for the present gate.
- `Unverified`: may be valid, but freshness or evidence is insufficient.
- `Stale`: its freshness rule expired or its references no longer resolve.
- `Superseded`: replaced by a newer accepted fact.
- `Invalidated`: known to be incorrect and forbidden as guidance.
- `Terminal`: completed, cancelled, rejected, or otherwise no longer active.
- `Historical`: retained for evidence, rationale, audit, or reproducibility.

`Stale` does not mean `wrong`; `Terminal` does not mean `delete`. Age or file length alone never authorizes removal.

## 2. Required Metadata

Every canonical document declares near the top:

```markdown
Status: Active | Draft | Superseded | Archived
Canonical For: <one narrow responsibility>
Last Reconciled: YYYY-MM-DD
Freshness Rule: <event rule; optional time fallback>
Archive Rule: <what leaves this view and where it goes>
```

Add where relevant:

- live views: `As Of`, and `Evidence Cutoff` when evidence matters;
- roadmap: `Plan Version`, plus `Supersedes` and `Change Reason` on material revision;
- stable contracts: `Contract Version`, `Effective From`, `Last Verified Against`;
- diagnostics: `Diagnostic Status`, `Resolved On`, `Resolution`;
- lessons: `Rule Status: Active | Superseded | Retired`.

Event-based refresh is mandatory. Suggested fallbacks: `PROGRESS.md` 7 inactive days, `TODO.md` 14 days, active multi-month plan 45 days. A timeout marks information unverified; it does not complete, cancel, archive, or delete it.

## 3. Live Views, Ledgers, and Contracts

| Class | Documents | Lifecycle |
| --- | --- | --- |
| Live views | `PROGRESS.md`, `TODO.md`, current roadmap view | Rewrite and compact as reality changes; do not append indefinitely |
| Factual ledgers | `RUN_REGISTRY.md`, terminal task archive | Append-oriented; preserve corrections and negative evidence |
| Stable contracts | PRD, interface/result, backend/evidence, app flow, team protocol | Keep current accepted truth; remove superseded alternatives from the active contract |
| Diagnostics | `doc/diagnostics/*.md` | Preserve evidence with explicit open/resolved/superseded/invalidated state |
| Lessons | `lessons.md` | Preserve real mistakes; retire obsolete prevention rules explicitly |

Git history normally preserves old wording. Do not create a second active-state file merely to save every snapshot.

## 4. Document Rules

### Agent entrypoint

Owns routing, read order, conflict priority, completion standard, and document map only. Current blocker/task/run details belong in their canonical owners. Use exactly one canonical entrypoint.

### `PROGRESS.md`

A materialized current snapshot, not a diary:

- exactly one current phase;
- exactly one trusted next action, normally referencing an active task ID;
- only current blocker, active artifacts/roots, evidence summary, forbidden actions, and stop-loss;
- resolved blockers leave the live section after durable facts move to diagnostics, ledgers, roadmap history, contracts, or lessons.

Before shortening it, promote every durable fact. A configurable size warning is a review trigger, not an automatic deletion rule.

### `TODO.md`

Contains active work only. Default active states: `Pending`, `Ready`, `In Progress`, `Blocked`, `Review`. Default terminal states: `Done`, `Cancelled`, `Superseded`, `Rejected`.

Every active row should name owner, dependency, next action, acceptance gate, evidence state, and last-touched date. A task is not terminal merely because code was written or activity stopped.

### `IMPLEMENTATION_PLAN.md`

Owns roadmap, phase meaning, entry/exit gates, accepted transitions, stage-level blockers, and fallback. It is not today's command list or complete task history. Compress completed stages into goal, passed gate, evidence, meaning, and date. Material roadmap change increments `Plan Version`.

### `RUN_REGISTRY.md`

Never erase a run because it failed or became inconvenient. Record terminal class, trust transition, artifact boundary, parser eligibility, and correction/invalidated links. Shard large ledgers while preserving a compact canonical index.

### Diagnostics

State `Open`, `Resolved`, `Superseded`, or `Invalidated`. Live documents link only diagnostics that currently affect work. Preserve any diagnostic needed to explain a claim, run class, security decision, or irreversible correction.

### Stable contracts

PRD, interface/result, backend/schema/evidence, app-flow, and team files contain current accepted rules. Proposed alternatives and live blockers do not remain mixed into them. Preserve high-impact superseded rationale through version control or a decision/change record.

### `TEAM.md`

Owns stable collaboration protocol, not current assignees, panes, or a running team log. Current owners stay in `TODO.md`; current team blocker stays in `PROGRESS.md`.

### `lessons.md`

Preserve the mistake, cause, and correction. When its future rule no longer applies, mark the rule superseded or retired rather than deleting the historical lesson.

## 5. Task Closeout

A terminal task may remain in `TODO.md` only during the same closeout operation:

1. verify its acceptance gate and evidence;
2. record final status/date/outcome and successor impact;
3. promote run, diagnostic, roadmap, contract, or lesson facts to their owners;
4. update dependent active tasks;
5. append the terminal record to `doc/archive/TASKS.md` or `doc/archive/tasks/<phase-or-year>.md`;
6. remove the terminal row from the active queue;
7. recompute the `PROGRESS.md` next action;
8. run the post-change audit.

Never archive a task while it is `Blocked`, `Review`, missing acceptance, missing evidence, needed by an unresolved gate, or ambiguous in final status.

The task archive is terminal-only and append-oriented. It must not contain active work or become a shadow queue.

## 6. Run and Stage Closeout

Run closeout records terminal state, trust, artifacts, reviewer/accounting state, related task changes, and diagnostics.

Stage closeout requires exit evidence, compresses accepted phase meaning, cancels/supersedes obsolete future tasks, reseeds the active queue, updates plan version/current stage, reconciles live state, and updates affected stable contracts.

Project closeout transfers or closes every active task, bounds final claims, preserves required evidence and lessons, and leaves a recoverable archive/index.

## 7. Cleanup Workflow

All cleanup follows this order:

1. **Protect**: inspect worktree and unrelated edits; ensure recoverability.
2. **Inventory**: list canonical documents, owner, status, freshness, archive rule, and active references.
3. **Detect**: find conflicts, duplicates, stale references, terminal tasks in live views, plan/phase drift, evidence gaps, and live-state pollution.
4. **Classify**: assign one lifecycle state to every suspect item.
5. **Manifest**: propose `Keep`, `Verify`, `Update`, `Promote`, `Archive`, `Invalidate`, or `Delete`.
6. **Promote**: move durable facts to their owner before removing an old copy.
7. **Apply safely**: reversible, high-confidence actions first; obtain approval for uncertain or destructive changes.
8. **Verify**: rerun the audit and report remaining active state, archives, invalidations, deletions, risks, and next action.

Cleanup manifest:

| ID | Source | Fact/task | Classification | Action | Destination/owner | Evidence | Active references/dependencies | Risk | Confidence | Approval? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## 8. Safe-Deletion Gate

Deletion is allowed only when every condition is true:

1. item is not current, active, blocked, under review, or required by an unresolved gate;
2. durable facts were promoted;
3. no active task, document, claim, artifact, or dependency needs it;
4. required evidence/rationale remains in a ledger, diagnostic, decision record, archive, or version control;
5. retention, reproducibility, legal, security, and audit rules permit deletion;
6. references were updated and verified;
7. deletion is recoverable, or the user explicitly approved irreversibility;
8. the post-cleanup audit passes.

If any condition fails, keep, verify, archive, or invalidate instead.

## 9. Cross-Document Invariants

A healthy project has:

- one owner per current fact;
- one current phase and one next action in `PROGRESS.md`;
- a matching active stage in the plan;
- a next action tied to an active task or explicit no-action blocker;
- no terminal task in the active queue after closeout;
- no active task in a terminal archive;
- every blocked/review task carrying its unblock/acceptance evidence boundary;
- every evidentiary run in `RUN_REGISTRY.md` with trust and artifact path;
- current accepted truth in stable contracts;
- invalidated/superseded material visibly non-current;
- open diagnostics reachable from affected live state/tasks;
- no archive functioning as an alternate queue.

## 10. Non-Standard Layouts

Do not duplicate files to satisfy the auditor. Add `projectos.audit.json`:

```json
{
  "documents": {
    "entrypoint": "00_READ_THIS_FIRST/AGENTS.md",
    "progress": "00_READ_THIS_FIRST/PROGRESS.md",
    "todo": "02_canonical_docs/TODO.md",
    "plan": "02_canonical_docs/IMPLEMENTATION_PLAN.md",
    "run_registry": "02_canonical_docs/RUN_REGISTRY.md"
  },
  "diagnostics_globs": ["02_canonical_docs/diagnostics/*.md"],
  "task_archive_globs": ["02_canonical_docs/archive/tasks/**/*.md"],
  "active_task_statuses": ["approval-blocked"],
  "thresholds": {"max_progress_lines": 250}
}
```

Configured paths must remain inside the project root. Status aliases extend the default vocabulary; they never weaken terminal/archive safety.
