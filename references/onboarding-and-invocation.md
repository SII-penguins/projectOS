# ProjectOS Onboarding and Invocation

This reference defines how ProjectOS should feel to a first-time user. Internal routing may be complex; the user-facing experience must be simple and progressive.

## 1. One Front Door

The user can begin with ordinary language. They do not need to know the skill name, internal modes, canonical file set, or project-management vocabulary.

Representative triggers:

| User says | Infer internally | First action |
| --- | --- | --- |
| “我想做/开发一个……” | New project | Understand outcome and inspect/research feasibility |
| “这是我的报告/需求/调研……” | Material-backed project | Extract facts, decisions, contradictions, and gaps |
| “TODO、Progress、计划冲突/过时了” | Existing-project maintenance | Read-only inventory and lifecycle audit |
| “接着上次的项目做，先确认现在的真实状态。” | Resume | Verify freshness, repo state, references, and allowed next action |
| “这个任务/阶段完成了” | Closeout | Verify acceptance/evidence, then close and compact |

Do not show these internal route names unless the user asks how ProjectOS works.

Explicit fallback invocation:

```text
$project-os <ordinary project request>
```

## 2. First-Turn Response Contract

The first ProjectOS response should normally contain only:

1. **Understanding** — one sentence explaining what the user appears to want.
2. **Current step** — one sentence explaining what ProjectOS will do now.
3. **Evidence action** — read supplied files/repository or research what can be verified.
4. **One question maximum** — only when a decision-critical answer is needed immediately.

Good:

> 我理解你想做一个《某游戏》的玩法 MOD，但目前还需要先确认该游戏版本和可用的 MOD 工具链。我会先检查官方/社区支持与技术限制；当前只需要你确认目标平台是 PC 还是主机。

Bad:

> 请选择 Explore/Create/Maintain/Resume/Closeout，并选择 Lean/Core/Research/Team Profile，然后回答下面 23 个问题。

Do not display the full document list, lifecycle taxonomy, or cleanup procedure before it becomes relevant.

## 3. Internal Router

Route from evidence, not keywords alone:

### Start a new project

Use when the user has an idea but no approved brief. Research external facts when needed, distinguish feasibility from preference, and produce a concise brief before proposing documents.

### Adopt supplied material

Use when a report, PRD, transcript, note set, or research packet already exists. Parse it before asking questions. Separate:

- verified facts;
- user-approved decisions;
- proposals or hypotheses;
- contradictions;
- unsupported claims;
- missing decision-critical information.

### Maintain an existing project

Use when canonical documents exist or the user reports stale/conflicting state. Audit read-only first, then present a cleanup manifest. Do not silently rewrite or delete.

### Resume

Use when prior work exists but may be stale. Verify current branch/worktree, document freshness, task ownership, paths/artifacts, and the old next action before continuing.

### Close out

Use when a task, run, stage, or project appears complete. Verify acceptance and evidence before terminal classification. Promote durable facts, archive terminal-only history, compact live views, and post-audit.

## 4. Progressive Gates

Show one gate at a time:

### Gate 1 — Understand

Output a compact understanding containing outcome, audience, scope boundary, known constraints, evidence available, and key unknowns. This is not yet a full project document.

### Gate 2 — Approve the Brief

Present a short Project Brief and ask the user to approve or correct it. Do not create the canonical document set before this gate unless the user explicitly supplied and approved an equivalent brief.

### Gate 3 — Approve the Document Map

Propose the smallest sufficient set of responsibilities. Explain why each file is needed and what is intentionally omitted. The user approves/corrects the map.

### Gate 4 — Generate/Reconcile

Create or update canonical documents, then run ownership/consistency/lifecycle checks.

### Gate 5 — Handoff

State what is now approved, what remains deferred, the first allowed task, and what implementation action is not yet authorized. Do not automatically begin coding unless requested.

Maintenance replaces Gates 1–3 with read-only audit → cleanup manifest → approval. Closeout replaces them with acceptance/evidence review → closeout manifest → post-audit.

## 5. Question UX

- Ask one question at a time when answers affect subsequent questions.
- Batch only short, independent confirmations when that clearly reduces friction.
- Provide a recommended option and why it is preferred.
- Explain the consequence of alternative choices.
- Allow “recommended,” “use sensible defaults,” or a short custom answer.
- Do not ask the user for facts that files, repository inspection, or public research can establish.
- Do not repeat answered questions.
- Stop once the current gate is safe to pass.

A gate should normally require no more than five accepted questions. More questions are allowed only when the gate is genuinely blocked; explain why rather than continuing an opaque interrogation.

## 6. Defaults and Deferral

A default is permitted only when it is:

- reversible;
- low risk;
- conventional for the domain;
- not a legal/safety/security/claim decision;
- recorded as an assumption.

Deferred items require an owner and due gate. Do not force early decisions that do not affect the current gate.

## 7. Avoid Over-Triggering

Do not invoke the full ProjectOS workflow for:

- a one-line typo or isolated small code edit;
- a single factual explanation;
- casual brainstorming with no request for durable planning;
- ordinary writing unrelated to project execution;
- a task already governed by a more specific skill unless the user also requests ProjectOS governance.

When uncertain, keep ordinary assistance lightweight. ProjectOS becomes appropriate when the user wants durable multi-session planning, canonical documents, evidence gates, project maintenance, or explicit use of `$project-os`.
