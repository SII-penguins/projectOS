---
name: project-os
description: ProjectOS turns non-trivial, long-running AI-assisted projects into a canonical documentation and lifecycle system. Use when users say they want to start or plan a project ("我想做/开发一个…", "把这份调研整理成项目计划"), organize or repair project docs ("TODO/PROGRESS/Implementation Plan 乱了"), resume an existing project, or close out a task/stage; also use for AGENTS.md, PROGRESS.md, TODO.md, IMPLEMENTATION_PLAN.md, RUN_REGISTRY.md, lifecycle reconciliation, and safe cleanup. Infer the workflow from natural language—the user does not need to know internal modes. Do not invoke for a small standalone code edit, a single factual answer, or casual brainstorming unless ProjectOS is explicitly requested.
---

# ProjectOS

Use this skill to turn a complex project into a maintainable AI collaboration documentation system. ProjectOS gives agents one canonical owner for every fact, one live-state source, one active task queue, one run ledger, one roadmap, and one team protocol.

## First-Time User Contract

The user never needs to learn ProjectOS modes, file names, or document profiles before starting.

Accept ordinary requests such as:

- “我想开发一个游戏 MOD，应该怎么开始？”
- “这是我的调研报告，帮我整理成一个可执行项目。”
- “这个项目的 TODO、Progress 和计划已经乱了，帮我整理。”
- “接着做这个项目，先确认现在做到哪里。”
- “这个阶段完成了，帮我收尾并整理文档。”

Infer the correct internal path. Do **not** present a mode menu by default and do not ask the user to choose `Explore`, `Create`, `Maintain`, `Resume`, or `Closeout`.

On the first response:

1. restate the understood intent in one sentence;
2. state the immediate next step in plain language;
3. inspect supplied/repository evidence before asking questions;
4. ask at most one decision-critical question, or proceed without a question when the next step is safe;
5. do not list the entire ProjectOS document set unless the user asks or the document-map gate is reached.

Explicit invocation remains available as a reliable fallback:

```text
$project-os 我想开发一个某某游戏的 MOD，请从需求澄清开始引导我。
```

Read `references/onboarding-and-invocation.md` for routing, first-turn behavior, and progressive onboarding.

## Guided Planning Gates

ProjectOS provides its own planning gates; it does not depend on a client exposing a native “Planning Mode.” Show the user only the current gate and what approval unlocks next.

### New idea or rough project

```text
Understand available evidence
→ research/feasibility when needed
→ close current-gate assumptions
→ present a concise Project Brief
→ user approves/corrects the brief
→ present the smallest sufficient document map
→ user approves/corrects the map
→ create canonical documents
→ consistency audit
→ stop at implementation handoff unless implementation was explicitly requested
```

### Supplied report, requirements, or prior research

Treat the material as evidence. Extract facts, decisions, proposals, contradictions, and open questions first. Do not re-ask answered questions. Then use the same brief → document-map → document-generation gates.

### Existing project or conflicting documents

```text
Read-only inventory/audit
→ classify Current/Unverified/Stale/Superseded/Invalidated/Terminal/Historical
→ present cleanup manifest
→ obtain approval for uncertain/destructive actions
→ promote durable facts and apply cleanup
→ post-cleanup audit
```

### Resume or closeout

Reconcile freshness and references before trusting old state. For closeout, verify acceptance/evidence, promote durable facts, archive terminal work, compact live views, and run the post-change audit.

## Assumption and Question Policy

The goal is not “zero uncertainty across the entire project.” The goal is **no unresolved decision-critical assumption before the gate that depends on it**.

For each unknown, choose one state:

- resolved from evidence;
- answered by the user;
- reversible low-risk default, explicitly recorded;
- deferred with owner and due gate;
- blocking the current gate.

Question rules:

- read or research available evidence before asking;
- ask one question at a time by default;
- ask only when the answer materially changes scope, architecture, cost, risk, acceptance, evidence, legal/safety boundaries, or cleanup safety;
- include a recommended answer and its trade-off when possible;
- normally ask no more than five accepted questions in one gate; if more remain, defer non-blocking items or explain why the gate cannot pass;
- stop questioning as soon as the current gate can proceed safely;
- when the user says “按合理默认值继续,” use only reversible, low-risk defaults and record them.

Read `references/interrogation-checklist.md` for domain-specific question coverage, but never dump the full checklist on the user.

## Smallest Sufficient Document Set

Do not require the user to select a named profile. Infer the smallest set of document responsibilities that the project actually needs.

Before creating files, show a compact document map containing:

- document path;
- canonical responsibility;
- why this project needs it;
- omitted responsibilities and reason.

A small project may combine responsibilities while preserving one owner per fact. Research, formal evidence, or multi-agent work may require the fuller set.

## Core Rules

1. **One fact, one canonical owner.** Other documents may link or summarize, but must not copy the full live state, task queue, run history, stable contract, or diagnostic analysis.
2. **Live views are not logs.** `PROGRESS.md`, `TODO.md`, and the current roadmap view must be compacted as reality changes.
3. **Promote before removing.** Move durable facts to their owner before deleting or archiving an old copy.
4. **Audit before cleanup.** Existing projects receive a read-only lifecycle audit before reconciliation, compaction, archival, or deletion.
5. **Evidence before completion.** Implementation activity is not completion until its acceptance gate passes.
6. **Age is not deletion evidence.** Stale means “verify and classify,” not “discard.”

Read `references/lifecycle-protocol.md` before maintaining, resuming, cleaning, or closing out an existing project.

## Operating Workflow

1. Infer the user's intent and current gate without exposing internal route names.
2. Read `references/onboarding-and-invocation.md` and `references/interrogation-checklist.md` as needed.
3. Inspect supplied materials and repository evidence before asking questions.
4. Close only decision-critical assumptions for the current gate; mark deferred items with owner and due gate.
5. For an existing project, run the read-only audit when local files are available and prepare a cleanup manifest before mutation.
6. Read `references/document-blueprints.md` before generating or refactoring documents.
7. Apply `references/hard-rules.md` as the final quality gate.
8. Use `references/example-output-skeleton.md` only as a scaffold; never invent project-specific state from it.
9. Update only the documents that own changed facts.
10. At task, run, or stage closeout, promote durable facts, update dependencies/evidence, archive only terminal information, compact live views, and re-run the audit.

## Standard Responsibilities

Create only responsibilities that exist:

- one canonical agent entrypoint: `AGENTS.md` by default, or `CLAUDE.md` for a Claude Code-only project;
- live state: `PROGRESS.md`;
- active work: `TODO.md`;
- roadmap: `doc/IMPLEMENTATION_PLAN.md`;
- run/result facts: `doc/RUN_REGISTRY.md`;
- long failure analysis: `doc/diagnostics/*.md`;
- stable product/research, interface/result, backend/evidence, runtime-flow, and team contracts as needed;
- real mistakes: `lessons.md`;
- terminal-only archives under `doc/archive/` when needed.

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

Non-standard repository layouts should declare `projectos.audit.json` instead of duplicating canonical files.

## Closeout Standard

A task is terminal only after acceptance and evidence are recorded. During closeout:

1. update final classification and evidence;
2. promote durable facts to their owners;
3. update dependent and successor tasks;
4. move only terminal tasks to the archive;
5. remove the terminal row from the active queue;
6. recalculate the live next action;
7. verify the archive contains no active work;
8. run the post-change audit.

## Quality Gate

Before handoff, verify:

- the first-time user was not forced to choose internal modes or document profiles;
- only current-gate questions were asked, normally one at a time;
- the user approved/corrected the brief and document map before files were created;
- every current fact has one owner;
- `PROGRESS.md` names one current phase and one valid next action;
- `TODO.md` contains active work only;
- no blocked/review task was archived as completed;
- no active task exists in an archive;
- plan stage and live phase agree;
- every run/result has a trust level and artifact boundary;
- stable contracts contain current accepted rules, not live blockers or proposed alternatives;
- no deletion occurred without the safe-deletion gate;
- the post-cleanup audit passes or remaining findings are explicitly accepted.

## Reference Files

- `references/onboarding-and-invocation.md`: natural-language routing, first-turn contract, and progressive guidance.
- `references/interrogation-checklist.md`: domain question bank; load only relevant sections.
- `references/lifecycle-protocol.md`: freshness, reconciliation, closeout, archival, compaction, and safe-deletion rules.
- `references/document-blueprints.md`: responsibilities and sections for the canonical document set.
- `references/team-blueprint.md`: durable multi-agent collaboration and handoff.
- `references/hard-rules.md`: conflict priority and forbidden shortcuts.
- `references/example-output-skeleton.md`: compact scaffold only.
- `references/evaluation-scenarios.md`: positive, negative, and first-turn behavior tests.

## Tooling

- Run `python scripts/audit_project_docs.py <project-root>` for a read-only lifecycle audit.
- Use `--config projectos.audit.json` for custom document layouts and archive paths.
- Run `python scripts/validate_skill.py <skill-dir>` before packaging this skill.
