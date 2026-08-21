---
name: project-os
description: ProjectOS creates and maintains canonical specification documents for complex AI-assisted projects, algorithm research, experiments, and multi-agent engineering work. Use when a user wants a repository documentation system with AGENTS.md, PROGRESS.md, TODO.md, IMPLEMENTATION_PLAN.md, RUN_REGISTRY.md, diagnostics, stable contracts, canonical ownership, lifecycle reconciliation, stale-document cleanup, closeout, safe archival, or evidence gates.
---

# ProjectOS

Use this skill to turn a complex project into a maintainable AI collaboration documentation system. ProjectOS gives agents one canonical owner for every fact, one live-state source, one active task queue, one run ledger, one roadmap, and one team protocol.

## Core Rules

1. **One fact, one canonical owner.** Other documents may link or summarize, but must not copy the full live state, task queue, run history, stable contract, or diagnostic analysis.
2. **Live views are not logs.** `PROGRESS.md`, `TODO.md`, and the current roadmap view must be compacted as reality changes.
3. **Promote before removing.** Move durable facts to their owner before deleting or archiving an old copy.
4. **Audit before cleanup.** Existing projects receive a read-only lifecycle audit before reconciliation, compaction, archival, or deletion.
5. **Evidence before completion.** Implementation activity is not completion until its acceptance gate passes.
6. **Age is not deletion evidence.** Stale means “verify and classify,” not “discard.”

Read `references/lifecycle-protocol.md` before maintaining, resuming, cleaning, or closing out an existing project.

## Workflow

1. Read `references/interrogation-checklist.md`.
2. Determine whether the user needs a new documentation system, a migration of stale/conflicting docs, or an update/closeout of an existing project.
3. Ask only high-impact missing questions about current state, active queue, roadmap, run history, stable contracts, team workflow, evidence boundaries, and cleanup risk. Mark unresolved decisions as `待确认项` with an owner and due gate instead of guessing.
4. For an existing project:
   - inspect the worktree and canonical entrypoint;
   - read `PROGRESS.md`, then `TODO.md`, then relevant owner documents;
   - run `scripts/audit_project_docs.py` when local file access is available;
   - classify suspect information as `Current`, `Unverified`, `Stale`, `Superseded`, `Invalidated`, `Terminal`, or `Historical`;
   - produce a cleanup manifest before editing;
   - require the safe-deletion gate before destructive removal.
5. Read `references/document-blueprints.md` before generating or refactoring documents.
6. Apply `references/hard-rules.md` as the final quality gate.
7. Use `references/example-output-skeleton.md` only as a scaffold; never invent project-specific state from it.
8. Update only the documents that own changed facts.
9. At task, run, or stage closeout, promote durable facts, update dependencies/evidence, archive only terminal information, compact live views, and re-run the audit.

## Standard Outputs

Generate or update this structure when its responsibilities exist:

- one canonical agent entrypoint: `AGENTS.md` by default, or `CLAUDE.md` for a Claude Code-only project;
- `PROGRESS.md`;
- `TODO.md`;
- `doc/IMPLEMENTATION_PLAN.md`;
- `doc/RUN_REGISTRY.md`;
- `doc/diagnostics/*.md` as needed;
- `doc/PRD.md`;
- `doc/FRONTEND_GUIDELINES.md`;
- `doc/BACKEND_STRUCTURE.md`;
- `doc/APP_FLOW.md`;
- `doc/TEAM.md`;
- `lessons.md`;
- terminal-only archives under `doc/archive/` when needed.

For smaller projects, omit documents only when their responsibility truly does not exist. Preserve the ownership and lifecycle model even when responsibilities are temporarily combined.

## Lifecycle Control

Every canonical document states:

```markdown
Status: <state>
Canonical For: <one narrow responsibility>
Last Reconciled: YYYY-MM-DD
Freshness Rule: <event rule and optional time fallback>
Archive Rule: <what leaves this view and where it goes>
```

Additional controls:

- `PROGRESS.md`: `As Of` and one trusted next action;
- `TODO.md`: owner, dependencies, next action, acceptance gate, evidence, last touched;
- `IMPLEMENTATION_PLAN.md`: `Plan Version` and explicit stage gates;
- stable contracts: `Contract Version`, `Effective From`, `Last Verified Against`;
- diagnostics: `Diagnostic Status` and resolution state;
- lessons: prevention-rule status when it can age.

Non-standard repository layouts should declare a deterministic `projectos.audit.json` document map instead of duplicating canonical files.

## Closeout Standard

A task is terminal only after acceptance and evidence are recorded. During closeout:

1. update the task's final classification and evidence;
2. promote run, diagnostic, roadmap, contract, or lesson facts to their owners;
3. update dependent and successor tasks;
4. move only terminal tasks to the archive;
5. remove the terminal row from the active queue;
6. recalculate the live next action;
7. verify that the archive contains no active work;
8. run the post-change audit.

Run and stage closeout use the corresponding checklists in `references/lifecycle-protocol.md`.

## Quality Gate

Reject documentation systems where one file tries to be live state, task queue, roadmap, run log, failure diagnosis, and stable contract at the same time.

Before handoff, verify:

- every current fact has one owner;
- `PROGRESS.md` names one current phase and one valid next action;
- `TODO.md` contains active work only;
- no blocked/review task was archived as completed;
- no active task exists in an archive;
- plan stage and live phase agree;
- every run/result has a trust level and artifact boundary;
- stable contracts contain current accepted rules, not live blockers or proposed alternatives;
- superseded/invalidated/snapshot information cannot be mistaken for current guidance;
- no deletion occurred without the safe-deletion gate;
- the post-cleanup audit passes or remaining findings are explicitly accepted.

## Reference Files

- `references/interrogation-checklist.md`: question bank for setup, migration, and research scoping.
- `references/lifecycle-protocol.md`: freshness, reconciliation, closeout, archival, compaction, and safe-deletion rules.
- `references/document-blueprints.md`: lifecycle-aware responsibilities and required sections for the canonical document set.
- `references/team-blueprint.md`: rules for `doc/TEAM.md` and durable multi-agent handoff.
- `references/hard-rules.md`: conflict priority, update/closeout protocol, and forbidden shortcuts.
- `references/example-output-skeleton.md`: compact scaffold for current views, ledgers, contracts, archives, and cleanup manifests.

## Tooling

- Run `python scripts/audit_project_docs.py <project-root>` for a read-only heuristic lifecycle audit.
- Use `--config projectos.audit.json` for custom document layouts and archive paths.
- Run `python scripts/validate_skill.py <skill-dir>` before packaging this skill.
