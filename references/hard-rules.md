# Ownership and Evidence Rules

Use these rules for the facts affected by the task. Filenames below are defaults; preserve the project's mapped owners and existing contracts.

## Resolve conflicts

Canonical ownership determines where a fact belongs, not which statement is automatically true. Reconcile contradictions with current code, artifacts, accepted decisions, and the user's instructions. Mark unresolved claims unverified instead of copying the preferred wording into every file.

| Fact | Default owner |
| --- | --- |
| Current phase, blocker, next action | `PROGRESS.md` |
| Active task status, ordering, dependencies, acceptance | `TODO.md` |
| Run/result history and trust | `doc/RUN_REGISTRY.md` |
| Roadmap, stage meaning and exit criteria | `doc/IMPLEMENTATION_PLAN.md` |
| Goal, scope, product or research claim | `doc/PRD.md` |
| Interface, mathematical definitions, presentation | `doc/FRONTEND_GUIDELINES.md` or a domain-named contract |
| Schema, runtime, evidence and artifact contracts | `doc/BACKEND_STRUCTURE.md` or a domain-named contract |
| Runtime sequence | `doc/APP_FLOW.md` |
| Stable collaboration protocol | `doc/TEAM.md` |
| Task-relevant document routing and local operating constraints | `AGENTS.md` (or the client's established entrypoint) |
| Observed mistakes and their prevention | `lessons.md` |

## Update changed facts

A run event changes the ledger. Update progress only if it changes live state, TODO only if it changes a task, and the roadmap only if it changes stage meaning or gates. Apply this same rule to other events; an event is not a reason to rewrite all documents.

Link summaries to their owners. A small project may put distinct responsibilities in sections of one file. Larger live queues, ledgers, and diagnostics need separate views when combining them would obscure the next action.

## Evidence and tasks

- Record acceptance and evidence proportionate to the claim. Keep local tests, simulated checks, live integration, and formal experiments distinct.
- Run records identify their artifacts or state that no artifact exists. Preserve failures and trust transitions. A successful parser or process exit does not itself establish a scientific claim.
- Active work needs an owner, dependencies, next action, and acceptance criteria. Record actual scope restrictions; do not invent a forbidden-actions list for every task.
- If evidence blocks a claim, suspend that claim and dependent work. Continue independent authorized tasks. Use a diagnostic when the reasoning needs a durable explanation, not for every typo or corrected path.
- Completion, cancellation, rejection, and supersession have different evidence. Cancellation needs its decision and successor impact; it does not require pretending an unfinished implementation passed acceptance.
- Evidence can lose validity after closeout. Preserve the historical assertion and its correction, then reconcile affected claims, gates and tasks through `references/lifecycle-transitions.md`; do not silently keep a withdrawn result as current evidence.

## Research contracts

When relevant to the current experiment, specify data provenance and splits, named baseline configurations, metric computation and aggregation, model/training configuration, resource budget, artifact retention, and failure handling. Keep adjustable values in configuration. Unneeded later-stage details may remain deferred.

Exploratory notebooks can support analysis; a formal reproducibility claim needs a usable reproduction path. Separate smoke, development, reporting, and full runs where those modes exist.

## Collaboration

Use `references/team-blueprint.md` for a requested or established team. A team protocol does not independently authorize delegation or spending. Preserve file ownership, handoffs, and any project-specific review requirement without imposing a resident reviewer on unrelated work.
