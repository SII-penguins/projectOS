# Before/after audit

These commands are standalone read-only diagnostics. For governed writes use `references/lifecycle-change.md`, which owns the before/after sequence. The tool is read-only; capture writes JSON only to stdout. Retain that stdout in a task-owned evidence directory outside project inputs, before the relevant edit. Do not redirect to an input or another task's evidence. Do not substitute committed HEAD for the working state.

```sh
python scripts/audit_project_transition.py capture /project
python scripts/audit_project_transition.py guard /project --before /owned-evidence/before.json
python scripts/audit_project_transition.py compare /project --before /owned-evidence/before.json
```

All commands accept `--config` with a config path inside the project, using the existing auditor layout. Capture records selected progress, TODO, plan and task-archive views, hashes, actual root and config; diagnostics, contracts, run artifacts and unrelated owners are not read or captured by this check; it rejects observed concurrent changes during reading. Guard is a point-in-time check before an edit, not a filesystem lock. Coordinate concurrent writers and inspect overlapping diffs; a passing guard never authorizes whole-file replacement. The caller owns baseline retention and access: snapshots contain document content.

A baseline from another worktree, damaged JSON/digest, or unavailable configured input is rejected. The digest detects accidental changes, not forgery, valid approval or scientific acceptance. A mapping change is reported for review rather than silently erasing coverage. With no baseline, do a current audit and state that transition safety was not checked; do not reconstruct an imaginary earlier state.

## Supported relations

Task tables use the same parser/config as the current-state auditor. The comparison retains all previously identified tasks, including unknown statuses conservatively. Every disappearing active task needs a retained terminal outcome, with a recognized nonempty evidence/decision field. A transfer/cancellation therefore retains its original attempt and links the successor or decision. This does not validate that decision's authority. Active acceptance changes and changed historical outcomes require review even if the ID survives. Terminal archive records may omit the former acceptance column: the retained baseline preserves that text; semantic closeout still needs review.

Important exits may use a table in the existing mapped plan, not a new tracker:

| Exit ID | Requirement | Status | Tasks | Decision | Owner | Revisit |
| --- | --- | --- | --- | --- | --- | --- |
| S1-G2 | Mechanism validated under accepted protocol | Open | T-004 | | lead | |

Recognized exit states: Open, Pending, Blocked, Review; Satisfied; Deferred, Transferred, Cancelled, Superseded. Open exits require active carrying tasks. Deferred/transferred exits need a decision reference, owner and revisit event. Other dispositions require an evidence/decision reference. Changed requirements or exit states remain review findings; their legitimacy cannot be inferred from nonempty text. An external dependency can be a Blocked carrying task with its owner and event. Downstream work does not silently satisfy upstream exits.

Missing/unsupported exit tables are reported as partial coverage, not a demand to restructure every historical document. Only explicitly structured exits are checked; free-text obligations and evidence-retraction consumers without structured bindings still require targeted human/model inspection. Do not claim all project obligations are covered just because the supported table passed.

## Results

- `checked`: supported task and explicit exit checks ran without findings; semantic/approval/artifact limits remain.
- `partial`: no detected finding but a declared check could not run.
- `review_required`: a change requires scope/evidence/decision review.
- `findings`: a structural inconsistency was found.
- `unchecked`: invalid/missing input or execution failure.

Exit codes: 0 checked (or successful capture/unchanged guard); 1 findings/review (or changed guard); 2 unchecked; 3 partial. A review finding is not proof of wrongdoing. Preserve its disposition in the existing owner; do not automatically revert legitimate changes or weaken the checker to make it green.
