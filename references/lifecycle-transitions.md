# Document and Evidence Transitions

Read the relevant section when creating an owner, changing its meaning/location, retracting evidence, reopening work, or recovering an interrupted cleanup. Ordinary edits do not need the entire protocol.

## Creation and adoption

Create a document when a fact needs durable ownership and no suitable owner exists. Use an existing section when it is sufficient. A new filename is not itself a new responsibility.

Identify responsibility, inputs/provenance, current decisions, and the event that should refresh the document. Distinguish observed facts, accepted decisions, proposals and assumptions. A researched proposal is not automatically an accepted contract; a user's explicit implementation request can already authorize routine implementation choices without another approval ceremony.

Mark draft contracts as Draft until they are adopted within the task's authority. Upon adoption, make the applicable version/effective point clear and update the routing source. Do not leave two competing current owners. For an existing project, inventory its actual owners before introducing defaults; migrating a file does not validate its contents.

## Separate lifecycle from confidence

Document lifecycle, evidence confidence, and task execution are independent dimensions. An archived result can still be valid evidence. An active contract can contain an explicitly unverified assumption. A completed task can later need corrective work. Do not force these into a single status vocabulary.

| Change | What to preserve and reconcile |
| --- | --- |
| Draft becomes an accepted contract | Applicable decision, version/effective point, affected implementation and validation tasks |
| Current owner becomes superseded | Successor link and effective boundary; references requiring the historical version stay version-specific |
| Information becomes stale | Mark the unsupported freshness, identify a verification action; do not infer falsehood or cancellation |
| Evidence is disproved or unavailable | Correction and provenance, affected claims, dependent tasks/stage gates and the remaining valid evidence |
| Task is completed/cancelled/superseded | Its particular outcome evidence or decision, dependency impact and retained history |
| Project is dormant or closed | Actual outstanding work, retention/location of evidence, reason and conditions for resumption |

`Last Reconciled` records a consistency check, not proof that every linked experiment was rerun. Record the source revision/run/config or applicable evidence cutoff for claims that depend on them. Do not make old evidence look fresh by only changing a date.

## Evidence correction and invalidation

Preserve the original run record and add a dated correction with its reason/source. Downgrade or retract the affected trust/claim; do not erase a failed run or rewrite historical success as if the original assertion never existed.

Trace actual consumers: claims, tables/reports, completed acceptance statements, stage exits and tasks that require the evidence. Update only affected owners. A completed report may need to be marked superseded or invalidated, while independent conclusions remain usable.

If a gate no longer has sufficient evidence, record that current boundary and open the smallest authorized corrective or verification task. Do not automatically rerun expensive experiments or change an accepted project goal because a document became stale. Continue independent authorized work.

## Reopen work without erasing history

Retain the previous terminal record and its evidence/decision. For the table-based auditor, give the new attempt a unique ID (for example `T-014-R2`) and link it to the prior `T-014` outcome with the reopening reason. Do not place the same attempt ID in both the active queue and archive.

Re-evaluate the new attempt's dependencies and acceptance. A cancelled or rejected prerequisite is not a successful result; either remove that prerequisite through an applicable decision, select an alternative, or keep dependent work blocked. If a project uses stable task IDs with an external attempt/version model, preserve it and state which semantics need direct review rather than forcing the auditor's table model onto it.

Reopening does not restore old paths, assignees, budgets or next actions without verification. A dormant project retains genuinely open tasks; inactivity alone never moves them to terminal history.

## Move, split, merge and retire owners

Preserve project-specific contracts and choose boundaries by update frequency and reader needs. For a split/merge, map each responsibility to its new owner before moving facts. Preserve task/run IDs and evidence links; do not mint new result identities merely because a file moved.

Copy/promote durable material first, update the document map and affected references, then retire the old owner. A small non-authoritative redirect can preserve old entry links when useful; it must identify the successor and must not duplicate current state. Historical snapshots remain labeled with their version and evidence cutoff.

Check references against the actual paths and headings after a move. Git history alone does not preserve an untracked log, external artifact, or inaccessible remote result; verify the recovery location before relying on it. Delete only under the safe-deletion conditions in `references/lifecycle-protocol.md`.

## Interrupted or concurrent changes

Before a multi-file transition, establish the relevant starting revision/state and a recoverable change set. Coordinate edits to shared owners; immediately before applying, check whether another participant changed the facts on which the transition depends. Reconcile overlapping changes instead of overwriting a whole file from an old snapshot.

Make cleanup repeatable: an already promoted fact or archived attempt does not need a second copy. If an archive row exists, compare its outcome and evidence before removing the active row; identical recorded outcomes can complete the interrupted move, while conflicting outcomes require reconciliation.

If work stops between promotion and retirement, leave a precise resume point describing completed and pending changes. On resume, inspect actual files, finish missing references/updates, and check affected consistency. Restore only damaged parts from the recoverable copy if repair is not possible; preserve unrelated newer edits.

The handoff should say what changed, which evidence remains valid, what is still open, and the next authorized action. A transition manifest can be temporary and need not become a permanent extra project log.

Terminal task ledgers contain only terminal outcomes. A separately labeled, dated recovery snapshot may contain what was active at that historical moment; it is not a second active queue. Keep such snapshots outside terminal-task archive globs and do not restore their old statuses as current without verification. Preserve a snapshot only when the transition needs that recovery evidence; do not create one for every ordinary edit.

Recovery updates unrelated queue rows only if their facts or dependencies changed. Their Ready status does not authorize executing them during a documentation-reconciliation request.
