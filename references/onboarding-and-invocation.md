# Starting and Resuming a Project

Use ordinary language to identify the requested outcome. This reference supplies decision aids, not mandatory turns or approvals.

| Request | Useful starting point |
| --- | --- |
| “我想开发一个长期项目，帮我规划。” | Outcome, scope, feasibility, constraints, and acceptance |
| “把这份调研整理成项目计划和规范文档。” | Extract facts, decisions, proposals, contradictions, and missing evidence |
| “TODO、PROGRESS 和计划冲突了，帮我整理。” | Inspect affected owners and reconcile against current evidence |
| “继续上次的项目。” | Verify the current state and next action, then continue authorized work |
| “这个阶段完成了，帮我收尾。” | Verify the outcome, preserve evidence, archive terminal tasks, update next action |

Explicit `$project-os` invocation works with the same scope. Mentioning a filename such as `AGENTS.md` or asking how ProjectOS works does not by itself call for project initialization. Ordinary coding, isolated edits, and casual brainstorming remain lightweight.

## Establish the outcome

Read supplied material and relevant repository evidence before asking the user to repeat it. Research external facts when feasibility depends on them. Separate observed facts, user decisions, proposals, and unknowns.

A brief can capture the goal, scope, constraints, acceptance, and unresolved decisions. Reuse an existing brief when it is adequate. If the user requests document creation, choose a small document map and create it using available evidence and material reversible assumptions. Present the map with the deliverable. Separate approval of the brief or map is needed only when the user requests staged review or a genuinely missing decision requires it.

For a rough idea, ask the most consequential missing question first. Do not fill a question quota. Batch short independent questions if that reduces friction; defer decisions that do not affect current work. The question bank is for finding a gap, not for quizzing the user on every field.

## Continue within the agreed scope

The requested result determines the stopping point. “Plan only” does not authorize implementation. “Plan and implement” includes implementation and the relevant checks; do not stop after the first draft to ask whether to continue.

For maintenance, inspect affected documents and establish a recoverable change set. A cleanup manifest may be an internal working table or part of delivery for already authorized reversible changes. Prepare the independent work before requesting any genuinely missing authorization for a specific consequential action.

Keep task status separate from execution authority. A request to reconcile or close out documents authorizes the necessary state/evidence corrections, not delivery of every Ready backlog item (including unrelated documentation tasks). Preserve those tasks. A request to resume implementation may authorize selecting the next applicable task; use the actual request and prior authorization, not readiness alone.

Apply user corrections to the active task while preserving completed work. A side question need not discard the original objective. Keep material changes to scope, acceptance, and dependencies in their owner documents.

For a project intended to continue across sessions, put conditional document routing and writeback in its existing agent entrypoint, following `references/document-blueprints.md`. Skill installation/invocation alone does not install a background watcher or guarantee every future coding turn reloads this skill.

Report the result, relevant evidence, unresolved dependencies, and a usable next action. Avoid turning the final answer into a reproduction of the entire document system.
