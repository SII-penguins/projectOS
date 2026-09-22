# Lifecycle Protocol

Use for the affected state when resuming, reconciling, cleaning, or closing out a project. Ownership says where a fact belongs; lifecycle says when it changes or becomes historical. Scale inspection to the request and preserve already authorized independent work.

## Information states

| State | Meaning |
| --- | --- |
| Current | Verified for the present decision |
| Unverified | May be valid; freshness or evidence is insufficient |
| Stale | Refresh rule expired or references no longer resolve |
| Superseded | Replaced by a newer accepted fact |
| Invalidated | Known incorrect; not current guidance |
| Terminal | Completed, cancelled, rejected, or superseded work with recorded outcome |
| Historical | Retained evidence or rationale |

Age, length, and a terminal status are not deletion evidence.

These labels describe different dimensions, not a single mandatory state machine: document lifecycle, confidence in a fact, and task execution can differ. For creation/adoption, evidence withdrawal, reopening, owner migration or interrupted cleanup, use the relevant section of `references/lifecycle-transitions.md`.

## Metadata and freshness

For separately maintained canonical documents, use this header or the project's established equivalent:

```markdown
Status: Active | Draft | Superseded | Archived
Canonical For: <responsibility or clearly owned sections>
Last Reconciled: YYYY-MM-DD
Freshness Rule: <events that require verification>
Archive Rule: <what leaves this view and where it remains accessible>
```

Live state adds `As Of`; roadmaps add `Plan Version`; contracts can add `Contract Version` and `Last Verified Against`; diagnostics use `Diagnostic Status`; lesson entries can use `Rule Status`. Combined documents may share metadata while keeping facts in distinct sections.

Refresh on relevant changes. Time fallbacks are review signals, not automatic transitions. Auditor defaults are 7 days for progress, 14 for TODO and 45 for plans, configurable to the project; missing or old dates mean verify, not delete.

## Keep views useful

- Progress contains current phase, blocker, next action, active artifacts and evidence boundary. Move durable resolved explanations to their owners.
- TODO contains active work: Pending, Ready, In Progress, Blocked, Review by default. It owns dependencies, task owners and acceptance.
- Roadmap owns phase meaning, stage gates, accepted transitions and fallback. Compress completed phases into outcome, evidence and meaning.
- Run ledgers preserve failures, artifact locations, trust transitions and corrections. Shard if needed behind a stable index.
- Contracts contain accepted rules. Diagnostics retain explicit open/resolved/superseded/invalidated state. Lessons retain mistake history while retiring obsolete prevention rules.
- Team documents hold stable collaboration rules, not current assignments or pane logs.

## Closeout

For a completed task, verify acceptance and evidence. For Cancelled, Rejected or Superseded work, record the decision, reason and successor impact instead of claiming successful implementation. Blocked, Review, or ambiguous work remains active.

Promote durable facts, update affected dependencies, preserve the terminal outcome in an archive, remove its active row, and update the resume point. Archived records may still be referenced by successor tasks; keep these references resolvable. Do not archive work that still needs execution, acceptance, or review.

Run closeout records outcome, trust and artifact boundaries. Stage closeout requires its exit evidence or a recorded decision to cancel/supersede it; reconcile affected roadmap and tasks. Project closeout resolves or transfers remaining work and preserves required evidence.

Check resulting consistency once the change is complete. Continue unrelated authorized work if one claim or task cannot close.

## Cleanup

Inspect the affected worktree, documents, references, evidence, and recoverability before changes. Classify questionable information, preserve durable facts, then apply authorized corrections. A compact manifest is useful for a multi-file migration; a wording fix needs only its diff. A manifest is not automatically another user approval gate.

Useful manifest fields are source, fact/task, classification, proposed action, destination, evidence, affected dependencies and any unresolved decision. Available actions: Keep, Verify, Update, Promote, Archive, Invalidate, Delete.

Ask only for authority or a consequential decision that is actually missing. Existing authorization carries forward. After changes, inspect the affected references and state; run the read-only auditor for the supported lifecycle checks.

## Safe-deletion gate

Before deleting an obsolete project record or file, verify:

1. It is not active, blocked, under review, or required by an unresolved decision.
2. Durable facts and required evidence/rationale have been preserved.
3. No active task, claim, artifact or dependency requires the original.
4. Applicable retention and reproducibility constraints permit removal.
5. References can be repaired without losing access to evidence.
6. The action is within existing authorization and recoverable, or irreversibility is explicitly authorized.

Then repair and verify affected references and state. The post-change audit is a verification step, not a pre-deletion condition that cannot yet be met. If it reveals damage, repair or restore from the recoverable copy. If a precondition is unresolved, keep, verify, archive or invalidate that item and continue independent changes.

A passing structural audit never certifies this gate; it cannot establish artifact contents, retention obligations, or semantic acceptance.

## Auditor layouts and limits

Map existing files instead of creating duplicate owners:

```json
{
  "documents": {
    "entrypoint": "00/AGENTS.md",
    "progress": "00/STATE.md",
    "todo": "02/WORK.md",
    "plan": "02/PLAN.md",
    "run_registry": "02/RUNS.md"
  },
  "task_archive_globs": ["02/archive/**/*.md"],
  "diagnostics_globs": ["02/diagnostics/*.md"],
  "active_task_statuses": ["approval-blocked"],
  "thresholds": {"max_progress_lines": 250}
}
```

String mappings select entire files. For combined documents, map each role to a `{ "path": "PROJECT.md", "section": "Active work" }` object so active tasks and historical rows remain separate. `archive` can map a terminal-history section. See `references/audit-format.md` for the supported schema, dependency interpretation, coverage and output boundary.

Inspect report coverage before interpreting a clean result: absent roles mean some checks did not run. The auditor does not validate experiment artifact contents, semantic acceptance or deletion authorization. Review unsupported structures directly.
