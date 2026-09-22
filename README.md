# ProjectOS

ProjectOS is an Agent Skill for planning long-running projects and maintaining trustworthy project state across sessions. It separates live work from historical evidence and gives every fact one canonical owner.

[中文说明](README.zh-CN.md)

## Use it

After installation, describe the result you need:

```text
$project-os Turn this research report into a usable project plan and create the minimum documents. Use reasonable defaults for routine details.
```

```text
$project-os Plan and implement this feature, then run the agreed checks.
```

```text
$project-os Reconcile the conflicting TODO, progress and roadmap against the current evidence.
```

```text
$project-os Plan this project only. Show the proposal before writing any files.
```

Explicit invocation is supported; implicit discovery is enabled where the client supports it. Mentioning a filename or making an ordinary small edit does not by itself call for project governance. ProjectOS does not switch the client's planning mode.

## What to expect

ProjectOS reads relevant supplied material, identifies scope and acceptance, then completes the authorized work. A brief and document map can be useful outputs, but do not introduce extra approval stops. Staged review still applies when requested. Questions are limited to missing decisions that matter now; independent work continues while a decision is pending.

Planning-only requests end with a usable plan. Requests including implementation continue through implementation and appropriate verification. Existing user instructions, project contracts and resource limits remain authoritative.

Only task-relevant references are loaded. The skill does not prescribe a question count, team size, resident reviewer or full-project reading list.

## Document model

Use the smallest useful set and preserve existing paths. These are default responsibilities, not mandatory files:

| Responsibility | Default owner |
| --- | --- |
| Local constraints and document routing | `AGENTS.md` |
| Current phase, blocker, next action | `PROGRESS.md` |
| Active tasks and acceptance | `TODO.md` |
| Roadmap and phase meaning | `doc/IMPLEMENTATION_PLAN.md` |
| Runs, artifacts and trust levels | `doc/RUN_REGISTRY.md` |
| Product/research and domain contracts | `doc/PRD.md`, domain-specific contract files |
| Durable failure reasoning | `doc/diagnostics/` |
| Collaboration rules, if needed | `doc/TEAM.md` |
| Actual mistakes and applicable prevention | `lessons.md` |
| Terminal outcomes | `doc/archive/` |

Small projects may combine responsibilities in clearly owned sections. Canonical ownership identifies where to update a fact; it is not proof that an old document is true. Resolve disagreements against current evidence.

## Lifecycle and cleanup

Live views stay compact. Run evidence preserves failures and trust transitions. Proposed, superseded, invalidated and historical information remains distinct from current accepted state.

Closeout preserves the outcome and updates dependencies before removing a terminal task from the live queue. Completed work needs acceptance evidence. Cancelled, rejected or superseded work needs its decision and successor impact. Blocked and review work remains active.

Before cleanup, inspect affected state and recoverability; promote durable facts before removing an obsolete copy. Deletion additionally requires no active dependency, retained evidence, applicable retention rules, and sufficient authorization. Age or a clean audit alone never establishes deletion safety. See [lifecycle protocol](references/lifecycle-protocol.md).

## Installation

Clone into the client's skills location with the skill's folder name:

```bash
git clone https://github.com/SII-penguins/projectOS.git project-os
```

For Codex, place the folder under your configured skills directory, normally `$CODEX_HOME/skills/project-os`. Preserve any existing installation changes when updating.

## Tooling

Python 3.10 or newer; standard library only.

```bash
python scripts/validate_skill.py .
python -m unittest discover -s tests -v
python scripts/audit_project_docs.py /path/to/project
```

The package validator checks metadata, resources and Python syntax. Unit tests check script behavior. Neither proves a model will follow a workflow; [behavioral scenarios](references/evaluation-scenarios.md) describe separate evaluations.

The lifecycle auditor is read-only with respect to the project. It checks supported Markdown structure, task tables, queue/archive consistency, task references, phase drift and trust-column presence. It does not inspect experiment artifact contents or certify completion/deletion. A wording-only edit does not need a full audit.

For an existing layout, use `projectos.audit.json`:

```json
{
  "documents": {
    "entrypoint": "00/AGENTS.md",
    "progress": "00/STATE.md",
    "todo": "02/WORK.md",
    "plan": "02/PLAN.md",
    "run_registry": "02/RUNS.md"
  },
  "task_archive_globs": ["02/archive/**/*.md"],
  "thresholds": {"max_progress_lines": 250}
}
```

Configured inputs must exist and remain within the project. Unmapped optional default files may be absent; `null` disables an optional role. `run` remains a legacy alias for `run_registry`. Status aliases cannot make active work terminal. See the lifecycle reference for other options.

JSON reports use `--format json`. Optional `--output /path/outside/project/report.json` must be outside the audited project. Exit codes: 0 for no findings at the chosen threshold, 1 for findings meeting `--fail-on`, 2 for invalid inputs or execution errors. Warnings still need interpretation; a zero exit code is not semantic certification.

## Design and evaluation

This revision applies the [GPT-6 Astra model guidance](https://developers.openai.com/api/docs/guides/latest-model) and Eric Provencher's [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra). See [review findings and validation](ASTRA_REVIEW.md).

The core ownership and evidence rules remain model-independent. The revision removes unnecessary process constraints rather than hardcoding a model or requiring an API migration.
