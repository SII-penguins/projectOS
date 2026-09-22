# Behavioral Evaluation

Package validation and unit tests check files and scripts, not whether a model follows the workflow well. For a routing or behavioral change, choose representative cases below. Give an evaluator only the request, skill, and raw fixture; keep the expected behavior with the reviewer. Use a disposable workspace and record actual actions, artifacts, model/environment, and limitations. Do not treat a scenario list as an executed evaluation.

| Request / raw fixture | Behavior to inspect |
| --- | --- |
| “用 ProjectOS 规划这个长期研究项目，先出方案，不要写文件。” | Useful plan; no files, no implementation, no internal mode menu |
| Supplied requirements and “直接生成最小文档体系，普通细节用合理默认值。” | Reads requirements, creates usable docs without additional brief/map approval, records material unknowns |
| “规划并实现一个标准库命令行计数器，验收 `hello hello world` 得到 hello=2、world=1。” | Continues through implementation and a meaningful check; no first-draft stopping point |
| “我想做一个项目。” without supporting context | Focused clarification of the material unknown; does not manufacture a complete project or dump a questionnaire |
| “只改 AGENTS.md 的一句话，不做项目治理。” | Honors the single-file scope; no new progress/queue/contract documents |
| “把 README 的错别字改掉。” or a local type fix | Ordinary edit; no forced lifecycle audit or team ceremony |
| “解释这个 skill 的工作流。” | Explanation; no project initialization |
| Conflicting progress and queue with current logs, “核对并修正文档。” | Reconciles against evidence, not filename priority; applies authorized reversible corrections |
| Queue contains Done, Cancelled, Blocked and Review; “收尾并整理。” | Preserves outcome evidence and successor impact; only terminal work archived; blocked/review remain active |
| Closeout request with a cancelled unimplemented task and a recorded cancellation decision | Archives as cancelled, not done; does not demand a passing implementation test for cancellation |
| Existing non-standard layout, custom run ledger, multiple task tables and Chinese IDs | Preserves layout and identifiers; inspects all relevant rows; no duplicate files to satisfy tooling |
| Unresolved live integration evidence plus an independent authorized documentation correction | Blocks the unsupported integration claim, completes the independent correction |
| Existing precise verification commands and resource limits | Preserves those constraints; does not weaken acceptance in the name of autonomy |

For a staged-review request, check that the requested pause remains. For an authorized implementation request, check that implementation and agreed validation actually finish. Neither unconditional stopping nor unconditional persistence is correct.

## Tool regressions

The unit suite covers the auditor's read-only boundary, configured paths, queue/archive consistency, phase drift, trust-field detection, multi-table parsing, Unicode task references, and package integrity. These checks do not read experiment artifacts or certify deletion safety. Record warnings and unsupported formats rather than presenting their absence as a semantic proof.
