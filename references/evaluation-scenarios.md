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
| One PROJECT.md contains current state, active work, roadmap and history; user requests closeout while preserving layout | Uses role-specific sections, does not mix archive/live rows or generate duplicate state files; reports actual audit coverage |
| A new correction invalidates the evidence behind a previously completed task and stage | Preserves original observations, marks affected claims/gates unsupported, opens a distinct corrective attempt, and respects run/resource limits |
| A terminal row was copied to the archive before an interrupted closeout | Compares existing evidence, finishes the missing queue/reference updates once, and does not append duplicate terminal records |
| The same documentation-recovery request has an unrelated Ready glossary/code task in the queue | Leaves that task active and unexecuted unless existing authorization actually includes delivering it; Ready is not permission |
| A current contract is replaced or split into new owners | Preserves effective/version boundaries, redirects and relevant history; verifies consumers rather than only renaming the file |
| An audit inspects no supported documents or only an entrypoint | Reports empty/partial coverage instead of calling the whole project validated |

For a staged-review request, check that the requested pause remains. For an authorized implementation request, check that implementation and agreed validation actually finish. Neither unconditional stopping nor unconditional persistence is correct.

## Tool regressions

The unit suite covers the read-only boundary, configured paths/sections, audit coverage, queue/archive consistency, dependency cycles/readiness, phase drift, trust-field detection, Markdown tables, Unicode task references, per-task freshness and package integrity. These checks do not read experiment artifacts or certify deletion safety. Record warnings and unsupported formats rather than presenting their absence as a semantic proof.
