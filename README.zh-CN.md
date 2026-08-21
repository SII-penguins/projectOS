# ProjectOS

ProjectOS 是一个 Agent Skill，用于把复杂、长期、由 AI 辅助推进的项目，整理成一套可维护的规范文档与生命周期系统。它将当前状态、活动任务、路线图、运行证据、稳定契约、故障分析和历史记录分开管理，避免旧信息、冲突信息或错误信息继续影响后续工作。

[English README](README.md)

## 它解决什么问题

长期 AI 项目经常会逐渐出现多份职责重叠的文档：

- `TODO.md` 同时堆积活动任务、已完成任务、阻塞任务和已经放弃的任务；
- `PROGRESS.md` 不断追加历史过程，最后变成日记，而不再是当前状态快照；
- `IMPLEMENTATION_PLAN.md` 混入每天执行的命令、局部修复过程和已经失效的旧计划；
- run 记录、diagnostics、团队记录和稳定契约之间互相冲突，却没有明确的清理与退出规则。

ProjectOS 通过两套互补机制解决这些问题：

1. **Canonical ownership（唯一权威归属）**：每个项目事实只能有一个权威 owner。
2. **Lifecycle management（生命周期管理）**：每条信息都有明确的进入、更新、失效、替代、收尾、归档和历史保留规则。

## 核心保证

- **一个事实，一个 canonical owner。** 其他文档可以引用或摘要，但不能复制完整的 live state、任务队列、run 历史、稳定契约或故障分析。
- **Live view 不是日志。** `PROGRESS.md`、`TODO.md` 和当前路线图视图必须随着现实变化不断压缩和更新。
- **有证据才能完成。** 写完代码或进程进入 terminal 状态，并不等于任务完成；必须通过 acceptance gate 并保存证据。
- **先迁移，再移除。** 在归档或删除旧副本前，必须先把仍有价值的事实迁移到正确的 canonical owner。
- **先审计，再清理。** 存量项目在修改前必须先进行只读清单与生命周期审计。
- **时间久不等于可以删除。** Stale 信息必须先核验和分类，不能因为过期或文档太长就自动删除。
- **不把内部模式强加给用户。** 第一次使用者只需用自然语言描述项目，ProjectOS 会自行判断内部工作流。

## 快速开始

将 Skill 安装到兼容 Agent Skills 的客户端后，可以直接使用自然语言：

```text
我想开发一个《某游戏》的玩法 MOD，我应该怎么开始？
```

```text
这是我的调研报告，请把它整理成一个可执行、可长期维护的项目。
```

```text
这个项目的 TODO、PROGRESS 和 IMPLEMENTATION_PLAN 已经互相冲突了，请安全审计并整理。
```

```text
继续这个项目，但在执行前先核验现在的真实状态。
```

```text
这个阶段已经完成，请帮我收尾、归档终止任务，并压缩当前状态文档。
```

需要稳定、明确地指定该 Skill 时，可以显式调用：

```text
$project-os 我想开发一个《某游戏》的 MOD，请从需求澄清开始引导我。
```

ProjectOS 不会要求第一次使用者先选择 `Explore`、`Create`、`Maintain`、`Resume` 或 `Closeout`。这些只属于内部路由实现。

## 第一次使用时会发生什么

ProjectOS 的第一轮回复通常只做四件事：

1. 用一句话复述它理解的项目目标；
2. 用简单语言说明当前先做哪一步；
3. 在提问前，优先读取用户提供的文件、仓库状态或可验证的公开资料；
4. 只有在下一步确实依赖用户决策时，最多提出一个关键问题。

它不应该一开始就：

- 展示完整文档体系；
- 一次抛出几十个问题；
- 要求用户选择文档 Profile；
- 未经批准直接生成全部文件；
- 未经授权自动开始实现。

## 渐进式规划工作流

对于一个新项目，ProjectOS 会按审批 gate 推进：

```text
理解现有证据
→ 必要时调研可行性
→ 只解决当前 gate 所依赖的关键假设
→ 输出简洁 Project Brief
→ 用户批准或修正 Brief
→ 提出最小充分文档地图
→ 用户批准或修正文档地图
→ 创建或整理 canonical 文档
→ 运行一致性与生命周期检查
→ 停在 implementation handoff，除非用户已经明确要求继续实现
```

目标不是把整个项目未来的所有未知问题一次性消灭，而是：

> **在某个 gate 依赖一项决策之前，不允许留下该 gate 所依赖的关键假设。**

问题默认一次问一个，只围绕当前 gate，并在该 gate 能安全推进后立即停止。可逆、低风险的事项可以采用明确记录的默认值；暂不影响当前阶段的问题可以延后，并记录 owner 和 due gate。

## Canonical 文档模型

ProjectOS 只创建项目真正需要的职责。在写文件前，它会先提出一份“最小充分文档地图”。

| 文档 | Canonical responsibility | 不能演变成 |
| --- | --- | --- |
| `AGENTS.md` 或 `CLAUDE.md` | Agent 入口、阅读顺序、冲突优先级、操作规则 | 项目百科或 live state 副本 |
| `PROGRESS.md` | 当前阶段、当前 blocker、可信 next action、活动产物、证据边界 | 日记、完整 run 日志或完整任务队列 |
| `TODO.md` | 活动任务、owner、依赖、验收标准、证据状态 | 已完成任务历史或路线图 |
| `doc/IMPLEMENTATION_PLAN.md` | 路线图、阶段意义、stage gate、已接受阶段迁移、fallback | 当天命令清单或详细 run 账本 |
| `doc/RUN_REGISTRY.md` | run/root/parser/result 事实账本与 trust 分类 | 长篇故障分析或当前 next action |
| `doc/diagnostics/*.md` | 长篇失败分析、reviewer accounting、流程或证据诊断 | 另一份 live-state 文件 |
| `doc/PRD.md` | 产品/研究目标、范围、claim、成功边界 | 当前 blocker 或任务列表 |
| `doc/FRONTEND_GUIDELINES.md` | 接口、数学定义、结果展示或用户行为契约 | 进度历史 |
| `doc/BACKEND_STRUCTURE.md` | Schema、runtime、evidence、parser、accounting 与模块契约 | run 历史或活动队列 |
| `doc/APP_FLOW.md` | 系统运行顺序、组件交互和数据流 | 当前状态报告 |
| `doc/TEAM.md` | 稳定的多 Agent 角色、并发、权限和 handoff 规则 | 持续追加的团队日志或当前 assignee 列表 |
| `lessons.md` | 真实错误、原因、修复和预防规则 | 通用规则百科 |
| `doc/archive/` | 只保存 terminal 任务或阶段历史 | Shadow active queue |

小型项目可以合并部分职责，但每个事实仍然只能有一个 owner。

## 生命周期模型

在修改存量信息前，ProjectOS 会先进行分类：

| 状态 | 含义 |
| --- | --- |
| `Current` | 已针对当前 gate 完成核验 |
| `Unverified` | 可能仍然有效，但 freshness 或 evidence 不足 |
| `Stale` | freshness rule 已过期，或引用已经无法解析 |
| `Superseded` | 已被新的 accepted fact 或 plan 替代 |
| `Invalidated` | 已知错误，禁止继续作为当前指导 |
| `Terminal` | 已完成、取消、拒绝或不再活动 |
| `Historical` | 因证据、原因、审计或复现价值而保留 |

每个 canonical 文档都应声明：

```markdown
Status:
Canonical For:
Last Reconciled:
Freshness Rule:
Archive Rule:
```

不同文档还会补充更具体的字段，例如：

- `Plan Version`
- `Contract Version`
- `Evidence Cutoff`
- `Diagnostic Status`
- `Rule Status`

## 任务 Closeout

任务只有在 acceptance gate 和 evidence 都通过后，才能进入 terminal 状态。收尾顺序如下：

```text
核验 acceptance 与 evidence
→ 记录最终 classification 和 outcome
→ 将 durable facts 迁入 canonical owner
→ 更新依赖任务和后继任务
→ 将 terminal 记录追加到 task archive
→ 从活动 TODO 队列移除
→ 重新计算 PROGRESS 中的可信 next action
→ 运行 post-change audit
```

以下任务不能归档：

- `Blocked`
- `Review`
- 缺少 acceptance evidence
- 仍被 unresolved gate 使用
- 最终状态存在歧义

archive 只能保存 terminal history，不能成为第二份活动任务队列。

## 安全清理

存量项目按照以下顺序整理：

```text
保护 worktree 与可恢复性
→ 清点 canonical 文档和引用
→ 检测冲突、stale state、重复信息和生命周期泄漏
→ 对每个可疑条目分类
→ 输出 cleanup manifest
→ 迁移 durable facts
→ 执行已批准的修改
→ 运行 post-cleanup audit
```

Cleanup manifest 只允许这些动作：

```text
Keep | Verify | Update | Promote | Archive | Invalidate | Delete
```

只有同时满足以下条件，才允许删除：

- 条目不再活动；
- 有价值的事实和证据已经保留；
- 没有活动依赖仍需要它；
- 所有引用已经修复；
- retention、复现、法律、安全和审计规则允许；
- 操作可恢复，或用户明确批准不可逆删除；
- post-cleanup audit 通过。

如果任一条件不满足，只能保留、核验、归档或标记失效，不能删除。

## 安装

建议把仓库克隆到名为 `project-os` 的目录，使目录名与 Skill name 一致：

```bash
git clone https://github.com/SII-penguins/projectOS.git project-os
cd project-os
```

随后按照所使用客户端的 Agent Skills 目录规则，将整个 `project-os/` 文件夹注册或复制到 Skill 目录中。

当客户端支持时，ProjectOS 可以隐式触发；需要确定性调用时，使用 `$project-os`。

## 验证与工具

验证 Skill 包：

```bash
python scripts/validate_skill.py .
```

运行回归测试：

```bash
python -m unittest discover -s tests -v
```

对已有项目执行只读生命周期审计：

```bash
python scripts/audit_project_docs.py /path/to/project
```

对于非标准仓库目录，不要为了满足审计器而复制 canonical 文件。应创建 `projectos.audit.json` 映射实际路径。

示例：

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

审计脚本是启发式、只读工具。它的 finding 只会触发核验，不会自动授权删除、归档或 terminal classification。

## 仓库结构

```text
SKILL.md                              核心触发与操作工作流
agents/openai.yaml                    客户端展示信息和默认提示词
references/onboarding-and-invocation.md
                                      第一次使用引导和自然语言路由
references/lifecycle-protocol.md      Freshness、closeout、archive 和 cleanup 规则
references/document-blueprints.md     Canonical 文档职责
references/interrogation-checklist.md 决策关键问题覆盖范围
references/hard-rules.md              冲突优先级和禁止事项
references/team-blueprint.md          多 Agent 协作协议
references/evaluation-scenarios.md    正向与反向触发测试场景
scripts/audit_project_docs.py         只读项目文档审计器
scripts/validate_skill.py             Skill 包验证器
tests/                                生命周期与调用引导回归测试
README.md                             英文 README
README.zh-CN.md                       中文 README
```

## 什么时候不应该使用 ProjectOS

以下情况不应强制进入完整 ProjectOS 流程：

- 修改一个错别字或独立的小型代码错误；
- 回答单一事实问题；
- 只是随意脑暴，没有建立长期项目的意图；
- 与项目执行无关的普通写作；
- 已有更具体 Skill 管理的任务，且用户没有要求 ProjectOS 治理。

ProjectOS 最适合：

- 跨多个 session 的长期工作；
- 多 Agent 或多人协作；
- 包含实验、run、evidence gate 或多个 stage 的项目；
- 文档持续演化，并且 stale information 会显著增加风险的项目。
