# ProjectOS

ProjectOS 是用于长期项目规划和状态维护的 Agent Skill。它让当前工作、历史记录和证据各有归属，便于跨会话继续推进项目。

[English README](README.md)

## 使用方式

安装后直接描述需要完成的结果：

```text
$project-os 把这份调研整理成可执行项目计划，并直接创建最小必要文档。普通细节用合理默认值。
```

```text
$project-os 规划并实现这个功能，完成约定的验证。
```

```text
$project-os 根据当前证据，修正互相冲突的 TODO、PROGRESS 和路线图。
```

```text
$project-os 先规划这个项目，只给方案，不要写文件。
```

支持显式调用；客户端支持时也允许隐式选择。提到某个文件名或进行普通小改动，并不自动触发整套项目治理。Skill 不会切换客户端的 Planning 模式。

## 工作方式

先读取与任务有关的材料，明确结果、范围和验收要求，然后完成已授权的工作。Brief 和文档地图可以作为工作产物，不再默认分别要求用户批准；用户明确要求分阶段审阅时，仍按要求暂停。

只询问当前工作真正需要、且无法从材料合理推断的决策。普通、可逆的选择可采用默认值，重要假设写清楚；某个问题未解决，不妨碍独立且已授权的工作继续。

“只出方案”以可用方案结束；“规划并实现”继续完成实现和适当验证。已有项目约束、验收命令、算力预算和用户授权保持有效。

按任务加载资料，不要求固定提问数量、固定团队规模、常驻 reviewer 或每次通读整个项目。

持续项目的入口会包含按变化触发的回写规则：事实变化时更新已有 owner，未变化的不重写。安装 ProjectOS 不等于启动后台监控，也不要求每次普通编码都执行完整生命周期流程。

## 文档职责

选择最小充分的结构，保留已有路径。下表是默认职责，不是必须生成的文件清单：

| 职责 | 默认归属 |
| --- | --- |
| 项目特有约束与文档路由 | `AGENTS.md` |
| 当前阶段、阻塞与下一步 | `PROGRESS.md` |
| 活动任务与验收 | `TODO.md` |
| 路线图与阶段意义 | `doc/IMPLEMENTATION_PLAN.md` |
| 运行、产物与证据可信度 | `doc/RUN_REGISTRY.md` |
| 产品／研究目标与接口契约 | `doc/PRD.md` 和领域契约文档 |
| 需要保留的故障分析 | `doc/diagnostics/` |
| 确有需要的协作规则 | `doc/TEAM.md` |
| 真实错误与适用的预防规则 | `lessons.md` |
| 已终止任务的结果记录 | `doc/archive/` |

小项目可将不同职责放在同一文件的独立章节，每条事实仍只有一个 owner。Owner 决定事实应在哪里更新，不保证旧文字正确；冲突需结合当前证据核实。

## 生命周期与清理

当前状态和活动队列保持精简；运行记录保留失败和可信度变化。提案、失效结论和历史材料应与当前已接受规则区分。

收尾先保留结果、更新依赖，再将终止任务移出活动队列。完成需要验收证据；取消、拒绝、替代需要相应决策及后继影响，不要求虚构实现成功。Blocked 和 Review 仍是活动工作。

清理前检查受影响状态和可恢复性，移除旧副本前迁移有效事实。删除还需核实活动依赖、证据保留、适用的留存约束及已有授权。仅凭文件过旧或审计通过，不能判定可删除。详见[生命周期规则](references/lifecycle-protocol.md)。

创建与采用、证据修正、任务重新开启、文档迁移和中断恢复的具体处理见[文档与证据状态迁移](references/lifecycle-transitions.md)。生命周期与可信度分开：归档的证据可能仍有效，曾经接受的结果也可能后来被推翻。重新开启保留原结果并创建新尝试；中断收尾从现有文件继续，不重复追加归档。

## 安装

将仓库放入客户端技能目录，并使用技能名称作为文件夹名：

```bash
git clone https://github.com/SII-penguins/projectOS.git project-os
```

Codex 通常使用 `$CODEX_HOME/skills/project-os`。更新已有安装时，保留本地修改。

## 验证与审计

需要 Python 3.10 或更新版本，无第三方依赖。

```bash
python scripts/validate_skill.py .
python -m unittest discover -s tests -v
python scripts/audit_project_docs.py /path/to/project
```

包验证器检查元数据、资源路径和脚本语法；单元测试检查脚本行为。模型行为另外使用[真实请求场景](references/evaluation-scenarios.md)评估，不把固定话术匹配当成行为证明。

审计器对项目只读，检查支持的 Markdown 结构、任务表、队列与归档冲突、任务引用、阶段漂移和 trust 列。它不会读取实验产物内容，也不能认证任务完成或删除安全。局部措辞修改只需检查相关 diff 和引用。

报告会列出实际检查的文件、章节和检查项。空扫描会报错；可选 owner 缺失意味着相关检查没有运行。依赖环、未满足的前置任务、含糊的下一步、重复归档和任务自身的过期日期也会被提示，不能用更新文档日期来掩盖旧任务。

非标准目录通过 `projectos.audit.json` 映射：

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

显式配置的输入必须存在且位于项目内部；未映射的可选默认文件可以不存在，也可用 `null` 禁用可选角色。兼容旧键 `run`，推荐使用 `run_registry`。状态别名不能把活动状态改成终止状态。

合并文档可使用 `"todo": {"path": "PROJECT.md", "section": "Active work"}` 和 `"archive": {"path": "PROJECT.md", "section": "History"}` 分别映射活动与历史章节；标题缺失或不唯一时会明确报错。完整规则见[审计格式与覆盖范围](references/audit-format.md)。

`--format json` 输出 JSON；`--output` 的报告路径必须在被审计项目之外。退出码：0 表示未达到指定失败阈值，1 表示 finding 达到 `--fail-on` 阈值，2 表示输入或执行错误。警告仍需按实际内容解释，退出码 0 不代表语义完全正确。

## 本次重新审查

本次修改依据 [GPT-6 Astra 官方模型指南](https://developers.openai.com/api/docs/guides/latest-model)和 Eric Provencher 的 [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)。具体问题与验证记录见 [ASTRA_REVIEW.md](ASTRA_REVIEW.md)。

所有权和证据规则仍适用于其他模型；调整的是妨碍完成任务的流程约束，没有硬编码模型或增加 API 迁移要求。
