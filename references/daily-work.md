# Daily work and project adoption

Use within an existing managed project when work changes its state, task result, contract or evidence. Ordinary isolated edits need only their relevant checks. A read-only request may inspect the queue but must not claim tasks or write back.

## Four checkpoints

| When | Smallest useful action |
| --- | --- |
| Start or recover | Confirm actual root/worktree, relevant task and acceptance, applicable contracts, current authority and unresolved dependencies. Reuse unchanged valid context. |
| Material fact changes | Replace the current assertion in its owner, preserve required provenance/history, and reconcile directly affected consumers. Do not append a conflicting second current assertion. |
| Before delivery | Match the result and evidence to the accepted scope; preserve every still-open obligation affected by removal, archival or phase change. Update the resume point if it changed. |
| Continue | Filter by authorization and constraints, then dependencies and the current goal's core gaps. Choose useful available work, or record the real wait condition. Ready is not authorization. |

No existing task: use the authorized request and existing owner to record necessary work, without inventing a new governance system. Single-executor projects need no lease ceremony; concurrent writers coordinate ownership before changing shared rows. Do not acquire another session's task merely because it appears idle.

Keep unchanged rows unchanged, including their Last Touched dates. A reconciliation date belongs to the affected owner; it is not a reason to refresh every task's timestamp or normalize partially accepted stages. Preserve the project's date/time convention when recording a real change.

A generic request to continue resumes the authorized scope, not a separately approval-blocked action. Resolve a recorded explicit hold only from an existing applicable grant or a new instruction that identifies that gated action; do not infer the missing grant from the task being next, feasible or low cost. If only held work remains, state the concrete decision needed and wait, with no unchanged-state writeback. Continue independent work when it already has authority.

A meaningful wait record names the dependency/event that could change the decision. Do not poll repeatedly without a reason, or start a new research direction to appear busy. No eligible work is a legitimate outcome.

## Preserve obligations and acceptance scope

Important stage exits can have stable IDs in the existing plan and task references in TODO. A partially accepted upstream result may enable downstream work while its remaining exits stay open. For affected exits, retain an active task, a recorded authorized deferral/transfer with owner and revisit event, or a tracked external dependency. Do not remove or weaken acceptance merely to obtain complete coverage.

For governed owner changes, use the single explicit entry in `references/lifecycle-change.md`; it captures and compares actual state around the bounded edits. The current-state auditor alone does not check this transition or the supported exit-state vocabulary. Do not use Git HEAD as a substitute for the actual working state. Review changed acceptance text even when IDs remain. Existing terminal archives must preserve the original attempt and outcome. Programmatic reference checks do not validate an approval or scientific result.

## Warning disposition and contracts

A finding affecting the next decision must be addressed in that affected scope. A deferrable maintenance finding gets a useful revisit trigger in an existing task or diagnostic, not another permanent alert system. Unsupported structure is an explicit coverage gap; it is not missing evidence. Repeated warnings should reuse their disposition rather than accumulating copies. Do not make every warning fatal.

Code establishes implemented behavior; accepted requirements establish intended behavior; evidence establishes demonstrated scope. When these disagree, locate the actual conflict and governing decision. Neither newest code nor an owner filename makes a claim true. Do not rewrite an accepted requirement to legitimize a defect, or reopen frozen work without a relevant evidence change or authorization.

## Adoption in an existing project

Resolve actual root, worktree, owner paths and effective AGENTS instructions, including overrides/nested scopes. Show a minimal additive integration diff that preserves the project's own approval, budget, frozen-scope and resource rules. Confirm the instruction really reaches a fresh session; file existence alone is insufficient. A skill upgrade does not update old entrypoints or inject instructions into running sessions.

At adoption, clarify whether necessary minimal state/evidence writeback is already part of authorized work. The template below applies only once consistent with the project's authority; it never overrides an explicit read-only request or restrictions on particular files. Existing same-scope approvals carry forward.

Suggested short entrypoint addition (adapt owner paths):

> For tracked work, consult the relevant task, acceptance and contract before acting. Within the authorized work, synchronize changed results, current blockers/actions and evidence boundaries to their existing owners; retire superseded current assertions and reconcile directly affected dependencies. Before delivery, preserve the affected unfinished obligations. No fact change needs no writeback; keep unchanged task rows and their Last Touched dates unchanged. Read-only work claims no task and edits no document. Use ProjectOS lifecycle references for complex archival, retraction or recovery. Do not expand scope, lower acceptance or execute unrelated Ready work during synchronization. Generic continuation does not lift a recorded explicit approval hold; reuse valid existing authorization and wait when the required specific decision is still missing.

Routine work need not reload the full skill if the effective entrypoint already provides the necessary rules. Hooks are optional and never replace this contract.

`python scripts/check_projectos_adoption.py /project --cwd /project/workdir` previews static instruction discovery and truncation. Supply actual global directory, fallback names and byte limit when known. It does not inspect or modify existing sessions and cannot prove host ingestion; keep that acceptance separate.
