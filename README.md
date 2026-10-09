# ProjectOS

**Keep a project's goals, current state, unfinished work, and evidence usable across AI sessions.**

ProjectOS is an Agent Skill for long-running work with Codex. It helps the agent pick up the right task, work within existing authorization, and update the project's own documents when facts change—so the next session can continue without reconstructing the whole conversation.

[中文指南](README.zh-CN.md) · [Install](#installation) · [Get started](#get-started) · [Reference guide](#reference-guide)

## When to use it

Use ProjectOS for work that spans sessions: research, software development, experiments, or a project with several open obligations and acceptance criteria.

It helps with:

- **Starting:** turn a goal and existing material into a practical plan and a small set of useful project documents.
- **Continuing:** find the current task, dependencies, applicable requirements, and existing authorization.
- **Keeping state current:** replace outdated conclusions, update the affected owners, and preserve evidence and unfinished obligations.
- **Closing or recovering work:** distinguish a finished run from an accepted task, retain partial results, and recover interrupted document changes.

A question, read-only review, or isolated typo fix stays small. ProjectOS does not require a new plan, task record, or lifecycle operation for every edit.

## Installation

Stable release: **[v2026.10.09.1](https://github.com/SII-penguins/projectOS/releases/tag/v2026.10.09.1)**.

In Codex, ask the built-in skill installer:

```text
Install the project-os skill from SII-penguins/projectOS at tag v2026.10.09.1.
The skill is at the repository root. If it is already installed, back up the
current version before replacing it and validate the installed package.
```

For a fresh manual installation:

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone --depth 1 --branch v2026.10.09.1 \
  https://github.com/SII-penguins/projectOS.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/project-os"
```

If `project-os` already exists, preserve that directory and any local changes before updating; do not overwrite it blindly. The release also includes a `project-os/` archive and a SHA-256 manifest. Python 3.10+ is required for the bundled command-line tools; they use the standard library. The optional Hook adapter requires POSIX file locking.

The installed skill is available for subsequent turns. Installing it does not modify your projects' `AGENTS.md` files or enable a global Hook.

## Get started

### 1. Start a project or adopt an existing one

Use an explicit request for the initial setup:

```text
Use $project-os to organize this project. Read the existing documentation first,
preserve its layout and approval rules, and propose the smallest useful plan
and document updates for this goal: [describe your goal].
```

For an existing project, keep its current authoritative files. Typical responsibilities are:

| Responsibility | Common location |
| --- | --- |
| Working rules and entry instructions | `AGENTS.md` |
| Current state, blockers, next action | `PROGRESS.md` |
| Active tasks, dependencies, acceptance | `TODO.md` |
| Phases and exit criteria | An existing plan |
| Accepted requirements | An existing specification or contract |
| Terminal outcomes and retained evidence | Existing archives or run records |

These are responsibilities, not mandatory filenames. A small project can combine them in clearly separated sections; custom paths can be mapped in `projectos.audit.json`.

### 2. Add a short project entry

To make everyday use implicit, add an instruction suited to the project's existing policy. For example:

> For tracked work, consult the relevant task, acceptance, contracts, and existing authorization before acting. Use ProjectOS when state or evidence needs reconciliation. Update the existing owners of changed facts, retire outdated current conclusions, and preserve unfinished obligations. Generic continuation does not lift an explicit approval hold. Reuse valid authorization; unchanged facts need no writeback. Keep read-only work and unrelated small edits within their requested scope.

Adapt this to the actual owner paths and project rules. Confirm that a new session receives the applicable instructions, including nested or worktree-specific overrides. See [adoption and daily work](references/daily-work.md).

### 3. Work in ordinary language

Once adopted, you can say:

| Request | Expected behavior |
| --- | --- |
| “Continue.” | Select eligible work from current obligations and authorization; wait if a specific approval is still missing. |
| “Fix this bug and run the agreed checks.” | Complete authorized work and synchronize changed results and verification sources. |
| “Read the failed run's receipt; do not retry.” | Record the actual outcome while retaining unmet acceptance and the retry boundary. |
| “Explain the current state without editing anything.” | Read and explain; leave project files unchanged. |
| “Only fix the typo in README.” | Make that edit without unrelated governance changes. |

You can still invoke `$project-os` explicitly whenever you want planning or reconciliation.

## Tools you can use

Run these from the installed `project-os` directory, substituting the actual project path.

**Read-only document audit:**

```sh
python -B scripts/audit_project_docs.py /path/to/project
```

For an existing custom layout:

```sh
python -B scripts/audit_project_docs.py /path/to/project \
  --config projectos.audit.json --format json
```

**Preview instruction discovery:**

```sh
python -B scripts/check_projectos_adoption.py /path/to/project \
  --cwd /path/to/project
```

This checks static discovery; it does not prove a running session has ingested the instructions.

**Make a governed document change:** use the scoped `projectos.change` tool if your host exposes it, or the bounded CLI described in [lifecycle changes](references/lifecycle-change.md). It captures before-state, checks proposed changes and drift, performs scoped writes, and records the actual result. It does not run arbitrary shell commands. Read-only explanations and unrelated prose edits do not need this entry.

## How to interpret results

A run ending, a task being complete, and an acceptance claim being supported are separate facts. A failed run can be terminal while its task remains blocked and its acceptance remains open.

An audit checks supported document structure. A change receipt binds an operation to recorded files and checks. Neither supplies authorization nor proves implementation correctness or research validity. Keep warnings that do not affect the decision in scope; resolve real contradictions without changing requirements or audit policy merely to obtain a clean report.

When evidence is withdrawn, correct the current claims and preserve the original observations as history. When a change is interrupted, compare the actual files and operation journal before resuming; do not roll back the entire workspace.

## Reference guide

| Need | Read |
| --- | --- |
| Plan or onboard a project | [Onboarding and invocation](references/onboarding-and-invocation.md) |
| Continue work and choose the next action | [Daily work](references/daily-work.md) |
| Choose a minimal document structure | [Document blueprints](references/document-blueprints.md) |
| Reconcile, archive, or close work | [Lifecycle protocol](references/lifecycle-protocol.md) |
| Retract evidence or reopen acceptance | [Lifecycle transitions](references/lifecycle-transitions.md) |
| Submit scoped changes and recover interruptions | [Lifecycle change entry](references/lifecycle-change.md) |
| Map custom files and understand audit coverage | [Audit format](references/audit-format.md) |
| Integrate optional host observations | [Host adapter](references/host-adapter.md) |

The optional adapter is for a deliberately configured host. It is not enabled by installation, does not create a background task runner, and does not guarantee that ordinary editing tools cannot bypass the entry. Recorded-input coverage also does not provide cross-file transactions or protection against every external concurrent writer.

### Enroll a project once for future sessions

The release includes `session_scope: "project"`. Enrollment is opt-in and depends on verified support in your actual working host. In the project's session, ask:

```text
Use $project-os to set up project-local hooks once with session_scope=project and observe mode,
so future sessions in this project join automatically. Preserve existing configuration; do not
enable global hooks or automatic continuation. Check the actual working host first and reuse
applicable host qualification. Verify this project's loading, exact trust and real event receipts
with one small fresh-session smoke check. Document disabling and existing-session exclusions.
```

The [shipped host qualification](references/host-qualification.json) covers the recorded Codex 0.161.0 desktop/local execution path; other environments need matching evidence. Publication and installation alone do not verify your project.

After one-time project configuration and host trust, new sessions need no allowlist update. The scope covers the configured root and ordinary subdirectories, excluding nested Git repositories/worktrees, external worktrees and symlink escapes. Enroll other worktrees separately. Use `excluded_sessions` to protect existing conversations. Existing allowlist profiles keep their behavior; bounded continuation still requires the original exact authorization mode. See [host setup](references/host-adapter.md#one-time-project-setup) for the profile and acceptance checks.

You can request setup from a session interrupted during document maintenance. Have the agent reread the actual installed Skill, inspect pending edits and operation journals, and preserve unfinished work instead of rolling back the repository or replacing its layout. Keep developer qualification in an isolated fixture; ordinary enrollment reuses matching evidence and checks one fresh project session. Do not reconstruct missing pre-edit snapshots for past turns. After configuration, host trust and any necessary reload, observation starts with subsequent turns that have complete events. If the old session cannot load the new configuration, continue in a new session rather than claiming a successful hot reload.

## Development and validation

```sh
python -B scripts/validate_skill.py .
PYTHONDONTWRITEBYTECODE=1 python -B -m unittest discover -s tests -v
```

Program tests, host integration checks, and model behavior evaluations establish different things. Release notes describe the evidence and its tested scope. Historical development reviews remain available in the repository; they are not the user guide or a promise of universal model reliability.
