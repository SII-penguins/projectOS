# Document Responsibilities

Use the responsibilities needed by the project, not a fixed bundle of filenames or headings. Preserve accepted contracts, evidence rules, and existing layouts. Create from inspected facts and user decisions; label proposals and material unknowns.

## Smallest useful set

A small project can start with an agent entrypoint and one planning/state document containing clearly owned sections. Split live state, active work, roadmap, and run evidence when their size or independent update frequency justifies it. Do not create empty research, frontend, or team documents for responsibilities that do not exist.

| Responsibility | Default file | Content that makes it useful |
| --- | --- | --- |
| Local instructions and document routing | `AGENTS.md` | Task-specific read pointers, unusual operating constraints, relevant verification commands |
| Current project state | `PROGRESS.md` | Current phase, blocker, next action, active artifacts, evidence boundary |
| Active work | `TODO.md` | Task ID, owner, status, dependencies, next action, acceptance, evidence, last touched |
| Roadmap | `doc/IMPLEMENTATION_PLAN.md` | Stage goals, entry/exit criteria, current stage, accepted transitions, fallback |
| Run evidence | `doc/RUN_REGISTRY.md` | Run/config identity, artifacts, outcome, trust, corrections and claim eligibility |
| Durable failure analysis | `doc/diagnostics/*.md` | Observations, cause, impact, correction, retained evidence, resolution status |
| Product/research contract | `doc/PRD.md` | Goal, scope, claims, success criteria and evidence boundaries |
| Interface or result contract | `doc/FRONTEND_GUIDELINES.md` | UI behavior or domain interfaces, metric and presentation definitions |
| Runtime/data contract | `doc/BACKEND_STRUCTURE.md` | Module, schema, artifact, environment and runtime constraints |
| Operating sequence | `doc/APP_FLOW.md` | Component/data/control flow and meaningful failure paths |
| Collaboration protocol | `doc/TEAM.md` | Stable ownership, resource limits, delegation and handoffs |
| Lessons | `lessons.md` | Observed mistake, cause, correction, future-rule applicability |
| Terminal history | `doc/archive/` | Final outcomes, evidence or cancellation decisions, successor links |

These names are defaults. For example, a research repository may use `METHOD.md` for its mathematical interface rather than a frontend-named file. Use `projectos.audit.json` to map supported auditor roles; do not rename established files merely to fit the examples.

## Agent entrypoint

Keep `AGENTS.md` short because clients may load it for every task. Put project-specific knowledge here, not a generic process manual. Route conditionally: progress and queue for resumed project work, schema docs for schema changes, deployment docs for deployment. An isolated edit should not trigger a whole-project reading sequence.

Declare the authoritative routing source. Preserve existing client-specific entrypoints and scoped instruction files; a compatibility shim may point to the canonical source. Do not duplicate substantive operating rules across clients.

Include only the verification commands and execution facts the project establishes. Do not copy a statement that tests are disposable or have no production access without checking it. Existing user scope and authorization controls the task; the document map does not add approvals.

## Live state and task queue

Use the lifecycle fields and transitions in `references/lifecycle-protocol.md` when maintaining live state. Keep a single current resume point; parallel lanes can be represented by task IDs in the queue without duplicating their descriptions in progress.

A live state should fit the actual project. The auditor's configurable size threshold is a warning, not a target word count. Empty sections and repeated historical summaries add no value.

For the auditor's structured task checks, use Markdown tables with `ID` and `Status`; include `Owner`, `Dependencies`, `Next Action`, `Acceptance Gate`, `Evidence`, and `Last Touched` when those details are tracked. Multiple task tables and Unicode IDs are supported. Map project-specific status aliases in config. For other formats, review the unsupported semantics directly rather than treating a clean report as proof.

## Roadmap and run ledger

A roadmap owns phase meaning, not today's commands. Keep a stable stage ID, one active stage where the project has a single roadmap, and evidence for accepted transitions. Retain completed stage meaning without copying the full task history.

Run evidence needs a run ID, configuration or commit, output path, observed outcome, and trust level. Choose a taxonomy appropriate to the project. A smoke run checks limited behavior; formal claim eligibility also depends on the project's accepted evidence standard. Do not turn a missing run into a placeholder result row.

## Contracts, diagnostics, and lessons

Keep accepted contracts separate from current blockers and proposed alternatives. Research contracts may need input/output definitions, data/split rules, baseline fairness, metric aggregation, training configuration and reproduction commands. Include details when relevant; do not require every project to describe an action space, parser, or legality oracle.

A diagnostic preserves reasoning that would otherwise be lost: observations, explanation, impact, correction and evidence. A routine path fix usually needs only the corrected owner and verification.

Lessons record real mistakes and when their prevention rule applies. Retire obsolete rules explicitly so one old failure does not constrain all future tasks.

Read `references/team-blueprint.md` only when defining collaboration. Stable team rules do not own live assignments and need not impose a reviewer or worker count.
