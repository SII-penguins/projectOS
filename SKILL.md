---
name: project-os
description: "Plan long-running projects and reconcile their canonical docs, live state, task queue, and closeout evidence. Use for durable planning or lifecycle maintenance, not ordinary coding or isolated instruction edits."
---

# ProjectOS

Keep project decisions, current state, work, and evidence usable across sessions with the smallest sufficient document set. Preserve established layouts and project-specific contracts.

## Scope and completion

Infer the requested outcome from the user's task and available evidence. Users do not need to select internal modes or document profiles. This skill does not switch the client's planning mode.

User instructions and existing authorization take precedence over these workflow suggestions, within system, developer, and execution constraints. A brief or document map is a work product, not an extra approval checkpoint. Complete the authorized outcome: planning-only work ends with a usable plan; implementation requests continue through the requested implementation and relevant verification.

Resolve questions from supplied material first. Ask only for missing decisions that materially affect the work and cannot reasonably be inferred. Use routine reversible defaults, record material assumptions, and continue independent authorized work while a decision is pending. Never invent project state, evidence, or authorization.

## Read by task

- Start or plan a project, including supplied research: `references/onboarding-and-invocation.md`.
- Resolve a specific planning uncertainty: relevant section of `references/interrogation-checklist.md`, a question bank rather than an interview script.
- Create or refactor project documents: `references/document-blueprints.md` and relevant rules in `references/hard-rules.md`.
- Resume, reconcile, archive, or close out project state: `references/lifecycle-protocol.md`.
- Design a team workflow when requested or already in use: `references/team-blueprint.md`.
- Need a concrete document example: relevant part of `references/example-output-skeleton.md`.
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
