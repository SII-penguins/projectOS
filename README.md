# ProjectOS

ProjectOS is an Agent Skill for turning non-trivial, long-running AI-assisted projects into a maintainable documentation and lifecycle system. It keeps current state, active work, roadmap, run evidence, stable contracts, diagnostics, and historical records separated so that old or conflicting information does not silently steer future work.

[中文说明](README.zh-CN.md)

## What Problem It Solves

Long-running AI projects often accumulate several partially overlapping documents:

- a `TODO.md` that mixes active, completed, blocked, and abandoned tasks;
- a `PROGRESS.md` that grows into a chronological diary instead of a current-state snapshot;
- an `IMPLEMENTATION_PLAN.md` that mixes roadmap decisions with daily commands and stale plans;
- run records, diagnostics, team notes, and stable contracts that disagree or age without a clear cleanup rule.

ProjectOS addresses this with two complementary controls:

1. **Canonical ownership** — every project fact has exactly one authoritative owner.
2. **Lifecycle management** — every fact has a defined way to enter, change, become stale, be superseded, close out, archive, or remain historical.

## Core Guarantees

- **One fact, one canonical owner.** Other documents may link or summarize, but do not duplicate complete live state, task queues, run history, contracts, or diagnostics.
- **Live views are not logs.** `PROGRESS.md`, `TODO.md`, and the current roadmap view are compacted as reality changes.
- **Evidence before completion.** Writing code or reaching a terminal process state does not make a task complete unless its acceptance gate and evidence pass.
- **Promote before removing.** Durable facts move to their canonical owner before an obsolete copy is archived or deleted.
- **Audit before cleanup.** Existing projects receive a read-only inventory and lifecycle audit before mutation.
- **Age is not deletion evidence.** Stale information must be verified and classified; it is not automatically wrong or disposable.
- **No hidden mode burden.** First-time users describe the project in ordinary language; ProjectOS infers the internal workflow.

## Quick Start

After installing the skill in a compatible Agent Skills client, you may start with ordinary language:

```text
I want to build a gameplay mod for <game>. How should I start?
```

```text
Here is my research report. Turn it into an executable project with a maintainable documentation system.
```

```text
TODO, PROGRESS, and IMPLEMENTATION_PLAN now conflict with each other. Audit and organize them safely.
```

```text
Resume this project, but verify the real current state before continuing.
```

```text
This stage is complete. Close it out, archive terminal work, and compact the live documents.
```

Explicit invocation is the reliable fallback:

```text
$project-os I want to build a mod for <game>. Guide me from requirements clarification.
```

ProjectOS does not ask a first-time user to select internal modes such as `Explore`, `Create`, `Maintain`, `Resume`, or `Closeout`. Those routes remain internal implementation details.

## First-Time User Experience

The first ProjectOS response should normally do only four things:

1. restate the understood intent in one sentence;
2. explain the immediate next step in plain language;
3. inspect supplied files, repository state, or verifiable public evidence before asking questions;
4. ask at most one decision-critical question when the next step truly depends on it.

It should not begin by showing the entire document set, asking dozens of questions, forcing a profile choice, or starting implementation without authorization.

## Guided Planning Workflow

For a new idea, ProjectOS progresses through approval gates:

```text
Understand available evidence
→ research feasibility when needed
→ close decision-critical assumptions for the current gate
→ present a concise Project Brief
→ user approves or corrects the brief
→ present the smallest sufficient document map
→ user approves or corrects the map
→ create or reconcile canonical documents
→ run consistency and lifecycle checks
→ stop at implementation handoff unless implementation was requested
```

The goal is not to eliminate every future unknown. The goal is to leave **no unresolved decision-critical assumption before the gate that depends on it**.

Questions are normally asked one at a time, limited to the current gate, and stopped as soon as that gate can proceed safely. Reversible low-risk defaults may be recorded explicitly; non-blocking decisions may be deferred with an owner and due gate.

## Canonical Document Model

ProjectOS creates only the responsibilities a project actually needs. It proposes the smallest sufficient document map before creating files.

| Document | Canonical responsibility | Must not become |
| --- | --- | --- |
| `AGENTS.md` or `CLAUDE.md` | Agent entrypoint, reading order, conflict priority, operating rules | Project encyclopedia or live-status copy |
| `PROGRESS.md` | Current phase, blocker, trusted next action, active artifacts, evidence boundary | Diary, complete run log, or full task queue |
| `TODO.md` | Active task queue, owner, dependencies, acceptance, evidence state | Completed-task history or roadmap |
| `doc/IMPLEMENTATION_PLAN.md` | Roadmap, phase meaning, stage gates, accepted transitions, fallback | Daily command list or detailed run ledger |
| `doc/RUN_REGISTRY.md` | Factual run/root/parser/result ledger and trust classification | Long diagnosis or current next action |
| `doc/diagnostics/*.md` | Long failure analysis, reviewer accounting, process or evidence diagnosis | Alternate live-state file |
| `doc/PRD.md` | Product/research goal, scope, claims, success boundaries | Current blocker or task list |
| `doc/FRONTEND_GUIDELINES.md` | Interface, mathematical, result-presentation, or user-facing behavior contract | Progress history |
| `doc/BACKEND_STRUCTURE.md` | Schema, runtime, evidence, parser, accounting, and module contracts | Run history or active queue |
| `doc/APP_FLOW.md` | Canonical operating sequence and component/data flow | Current status report |
| `doc/TEAM.md` | Stable multi-agent roles, concurrency, permissions, and handoffs | Running team log or current assignee list |
| `lessons.md` | Real mistakes, causes, corrections, and prevention rules | General rule encyclopedia |
| `doc/archive/` | Terminal-only task or phase history | Shadow active queue |

Smaller projects may combine responsibilities, but each fact must still have one owner.

## Lifecycle Model

ProjectOS classifies suspect information before editing it:

| State | Meaning |
| --- | --- |
| `Current` | Verified for the present gate |
| `Unverified` | May be valid, but freshness or evidence is insufficient |
| `Stale` | Its freshness rule expired or its references no longer resolve |
| `Superseded` | Replaced by a newer accepted fact or plan |
| `Invalidated` | Known to be incorrect and forbidden as current guidance |
| `Terminal` | Completed, cancelled, rejected, or otherwise no longer active |
| `Historical` | Retained for evidence, rationale, audit, or reproducibility |

Every canonical document should state its responsibility, reconciliation date, freshness rule, and archive rule. Relevant documents add more specific metadata such as plan version, contract version, evidence cutoff, diagnostic status, or lesson-rule status.

## Task Closeout

A task becomes terminal only after its acceptance gate and evidence are verified. Closeout then follows this order:

```text
Verify acceptance and evidence
→ record final classification and outcome
→ promote durable facts to their canonical owners
→ update dependent and successor tasks
→ append the terminal record to the task archive
→ remove it from the active TODO queue
→ recalculate the trusted next action in PROGRESS
→ run the post-change audit
```

A task must not be archived while it is blocked, under review, missing acceptance evidence, required by an unresolved gate, or ambiguous in final status.

## Safe Cleanup

Existing projects use this reconciliation sequence:

```text
Protect worktree and recoverability
→ Inventory documents and references
→ Detect conflicts, stale state, duplicates, and lifecycle leaks
→ Classify each suspect item
→ Present a cleanup manifest
→ Promote durable facts
→ Apply approved actions
→ Run a post-cleanup audit
```

The cleanup manifest uses explicit actions:

```text
Keep | Verify | Update | Promote | Archive | Invalidate | Delete
```

Deletion is permitted only when the item is inactive, its durable facts and evidence are preserved, no active dependency needs it, references are repaired, retention rules allow removal, the operation is recoverable or explicitly approved, and the post-cleanup audit passes.

## Installation

Clone the repository into a directory named `project-os` so the folder matches the skill name:

```bash
git clone https://github.com/SII-penguins/projectOS.git project-os
cd project-os
```

Then register or copy the `project-os/` folder into the skills location used by your Agent Skills-compatible client.

The skill supports implicit invocation where the client permits it. Use `$project-os` when you need deterministic explicit invocation.

## Validation and Tooling

Validate the skill package:

```bash
python scripts/validate_skill.py .
```

Run the regression suite:

```bash
python -m unittest discover -s tests -v
```

Run a read-only lifecycle audit against an existing project:

```bash
python scripts/audit_project_docs.py /path/to/project
```

For a non-standard repository layout, add a `projectos.audit.json` file that maps canonical documents and archive paths instead of duplicating files merely to satisfy the auditor.

Example:

```json
{
  "documents": {
    "entrypoint": "00_READ_THIS_FIRST/AGENTS.md",
    "progress": "00_READ_THIS_FIRST/PROGRESS.md",
    "todo": "02_canonical_docs/TODO.md",
    "plan": "02_canonical_docs/IMPLEMENTATION_PLAN.md",
    "run_registry": "02_canonical_docs/RUN_REGISTRY.md"
  },
  "task_archive_globs": ["02_canonical_docs/archive/tasks/**/*.md"],
  "thresholds": {"max_progress_lines": 250}
}
```

The audit script is heuristic and read-only. Its findings trigger verification; they do not authorize automatic deletion or terminal classification.

## Repository Layout

```text
SKILL.md                              Core trigger and operating workflow
agents/openai.yaml                    Client-facing metadata and default prompt
references/onboarding-and-invocation.md
                                      First-time routing and progressive guidance
references/lifecycle-protocol.md      Freshness, closeout, archival, and cleanup rules
references/document-blueprints.md     Canonical document responsibilities
references/interrogation-checklist.md Decision-critical question coverage
references/hard-rules.md              Conflict priority and forbidden shortcuts
references/team-blueprint.md          Multi-agent collaboration protocol
references/evaluation-scenarios.md    Positive and negative trigger scenarios
scripts/audit_project_docs.py         Read-only project documentation audit
scripts/validate_skill.py             Skill package validator
tests/                                Lifecycle and invocation regression tests
README.md                             English README
README.zh-CN.md                       Chinese README
```

## When Not to Use ProjectOS

Do not force the full ProjectOS workflow for:

- a one-line typo or isolated small code edit;
- a single factual explanation;
- casual brainstorming with no request for durable planning;
- ordinary writing unrelated to project execution;
- a task already governed by a more specific skill unless ProjectOS governance is also requested.

ProjectOS is most useful when work spans multiple sessions, agents, experiments, stages, evidence gates, or evolving documents—and when stale information would materially increase project risk.
