---
name: project-os
description: "Plan long-running projects and reconcile their canonical docs, live state, task queue, and closeout evidence. Use for durable planning, lifecycle maintenance, or state/acceptance changes in an already managed project. Keep isolated edits lightweight."
---

# ProjectOS

Keep project decisions, current state, work, and evidence usable across sessions with the smallest sufficient document set. Preserve established layouts and project-specific contracts.

## Scope and completion

Infer the requested outcome from the user's task and available evidence. Users do not need to select internal modes or document profiles. This skill does not switch the client's planning mode.

User instructions and existing authorization take precedence over these workflow suggestions, within system, developer, and execution constraints. A brief or document map is a work product, not an extra approval checkpoint. Complete the authorized outcome: planning-only work ends with a usable plan; implementation requests continue through the requested implementation and relevant verification. Queue status is not execution authorization: reconciliation or closeout does not itself authorize completing unrelated Ready tasks. A generic continuation resumes already authorized work; it does not grant a pending explicit approval or lift a recorded authorization hold. A new grant must identify the gated action clearly enough to resolve that hold. Reuse existing same-scope grants; do not invent an approval gate for ordinary authorized work.

Resolve questions from supplied material first. Ask only for missing decisions that materially affect the work and cannot reasonably be inferred. Use routine reversible defaults, record material assumptions, and continue independent authorized work while a decision is pending. Never invent project state, evidence, or authorization.

## Daily work in an adopted project

Before changing tracked work, confirm its task, applicable contracts, acceptance and authority from the smallest relevant owner set. Reuse still-valid context. On a material change, update the fact's owner, retire the superseded current statement, and reconcile directly affected dependencies. Before delivery, check the outcome, evidence boundary and remaining obligations; when continuing, choose authorized work against those obligations and dependencies. No changed fact means no repeated writeback. Read-only requests do not claim tasks or edit owners.

Write back only facts changed within each document's responsibility. Leave unchanged documents, task rows and already correct terminal records byte-for-byte, including metadata and dates: reading them, passing an audit or observing a date warning is not a fact change. Receipt-only reconciliation updates run, task and current-state owners; retain the raw reported status and evidence limits there, preserving accepted contracts and their verification provenance rather than treating an operational receipt as contract verification. An accepted contract does not cancel a separate open roadmap obligation. Do not repurpose an Open exit ID to a different requirement merely because its task link appears wrong or stale. Preserve the original requirement and Open state in a current carrying or review task until an explicit owner decision identifies that original requirement and its disposition; add a separate contract obligation rather than replacing the old one. A historical snapshot or a layout-correction rationale does not discharge the current obligation. Inspect the actual diff before delivery for these preservation boundaries.

For changes to task state, open obligations, carrying tasks, acceptance, authorization dependencies or terminal archives, submit the explicit scoped replacements through `projectos.change` when the host exposes it. Otherwise use `scripts/lifecycle_change.py` with a private state directory and a JSON request. This single entry captures real before-state, validates the proposal, guards drift, applies bounded edits and compares the actual result. When completion changes implementation-verification facts, include the existing Active contract provenance through the entry's narrow `verification_updates` operation; inspect actual test evidence, applicable scope and necessary summaries first. Unrelated/unchanged/unverified records need an explicit retention rationale, not a date refresh. Read `references/lifecycle-change.md` for the small request contract and recovery. Do not edit governed state first and attach a receipt afterward. An applied receipt proves only the executed checks and recorded coverage; resolve findings and review semantics/authority separately. Read-only explanations and unrelated text edits do not need a lifecycle write.

For documentation-only reconciliation or closeout, keep implementation and experiments pending separate authorization unless that authority already exists. The current Next Action must retain that dependency; a corrected diagnosis or a Ready task does not grant it. Update the carrying task's authorization dependency only within the task being reconciled when its facts change. When restoring the recovery point to an untouched queued task, state the authorization wait in the changed current-state owner and leave that task row byte-for-byte; closeout does not authorize adding reminders to unrelated rows.

Use `references/daily-work.md` for adoption, missing tasks, obligation coverage, warning disposition and next-action selection. Complex transitions still use the existing lifecycle references. Skill selection frequency is not a completion metric.

## Read by task

- Start or plan a project, including supplied research: `references/onboarding-and-invocation.md`.
- Resolve a specific planning uncertainty: relevant section of `references/interrogation-checklist.md`, a question bank rather than an interview script.
- Create or refactor project documents: `references/document-blueprints.md` and relevant rules in `references/hard-rules.md`.
- Resume, reconcile, archive, or close out project state: `references/lifecycle-protocol.md`; it routes advanced transitions and audit formats when needed.
- Design a team workflow when requested or already in use: `references/team-blueprint.md`.
- Need a concrete document example: relevant part of `references/example-output-skeleton.md`.
- Add optional host reminders or one-time project enrollment for future sessions: `references/host-adapter.md`. Project enrollment is explicit and observe-only; installing this Skill does not activate hooks.
- Evaluate this skill: `references/evaluation-scenarios.md`.

Load references that affect the current task; linked resources are not a reading checklist.

## Invariants

- One fact, one canonical owner. Other views link or summarize. Ownership tells you where to correct a fact; it does not make stale text true.
- Inspect affected state before cleanup. Promote durable facts before removing an obsolete copy, and preserve recoverability and active dependencies.
- Keep live state and active queues compact. Archive only terminal work with its outcome evidence; blocked and review work stays active.
- Distinguish accepted contracts, proposals, invalidated claims, and history. Preserve evidence trust levels: smoke checks do not prove formal research or live integration results.
- Update owners of changed facts. Small projects may combine responsibilities in clearly separated sections; do not create unused files or duplicate live state to fit a template.

## Verification

For lifecycle reconciliation, `python scripts/audit_project_docs.py <project-root>` checks supported document structure and cross-references without modifying the project. Use `--config projectos.audit.json` for a custom layout. Findings guide inspection; a clean report does not prove acceptance, artifact contents, or deletion safety. For a wording-only change, inspect the affected diff and links.

When changing this skill, run `python scripts/validate_skill.py <skill-dir>` and checks appropriate to the change. Package checks do not establish model behavior; use the evaluation scenarios for behavioral changes. After required checks pass, expand or repeat only for a new change, failure, or unresolved concern.

Use the lifecycle entry for governed changes described above; preserve its actual host call/return and unresolved coverage. Direct edits remain technically possible without a managed host, but cannot claim the entry's checks. The existing `audit_project_transition.py capture/guard/compare` commands remain read-only diagnostics; they do not retroactively supply an entry execution receipt. A missing baseline or unsupported structure is unverified, not a pass.
