# ProjectOS Trigger and Onboarding Evaluation Scenarios

Use these scenarios before merging invocation changes. Evaluate both whether ProjectOS should trigger and whether its first response follows progressive onboarding.

## Positive implicit triggers

| Prompt | Expected behavior |
| --- | --- |
| “我想开发一个《某游戏》的 MOD，我应该怎么做？” | Trigger; infer a new project, state the first feasibility step, ask at most one critical question; no mode menu |
| “这是我的调研报告，请整理成一个可执行项目和规范文档。” | Trigger; read/extract the report before questioning; brief gate before document generation |
| “TODO、PROGRESS 和 IMPLEMENTATION_PLAN 已经互相冲突，帮我整理。” | Trigger; read-only audit and cleanup manifest before mutation |
| “接着上次的项目做，先确认现在的真实状态。” | Trigger; freshness/repository reconciliation before trusting old next action |
| “这个阶段已经完成，帮我收尾。” | Trigger; acceptance/evidence check, closeout, compaction, post-audit |
| “用 ProjectOS 帮我规划这个长期研究项目。” | Explicit trigger; full relevant workflow |

## Negative or lightweight cases

| Prompt | Expected behavior |
| --- | --- |
| “把 README 里的一个错别字改掉。” | Do not force ProjectOS ceremony |
| “解释一下什么是 REST API。” | Do not trigger |
| “随便脑暴几个游戏点子。” | Ordinary brainstorming unless the user asks to turn one into a durable project |
| “帮我写一封项目延期邮件。” | Use writing workflow, not ProjectOS |
| “修复这个局部函数的类型错误。” | Use ordinary coding workflow unless it affects a governed long-running project and the user requests doc sync |

## First-response assertions

For every positive scenario:

- no request to choose internal modes;
- no request to choose a named document profile;
- one-sentence intent reflection;
- one current step;
- supplied evidence inspected before questions;
- no more than one decision-critical question on the first turn;
- no full document list before the document-map gate;
- recommended answer/trade-off when asking;
- no file creation or destructive cleanup before the relevant approval gate.

## Interrogation assertions

- closes decision-critical assumptions for the current gate, not every future unknown;
- normally no more than five accepted questions per gate;
- supports reversible defaults and explicit deferral;
- stops when the current gate can proceed;
- never asks the user to rediscover facts available in files, repository state, or public sources.

## Regression assertions

- explicit `$project-os` invocation remains recognized;
- maintenance retains Patch A read-only audit and safe-deletion gates;
- small tasks remain lightweight;
- long Chinese task IDs and non-standard repository layouts remain supported;
- lifecycle audit remains read-only.
