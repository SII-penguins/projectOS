# ProjectOS Astra review — 2026-09-22

## Sources and baseline

The two requested primary sources were fetched and read in full before repository review:

- OpenAI, [Using GPT-6 Astra](https://developers.openai.com/api/docs/guides/latest-model), including the complete model guide and migration section. The model-specific Markdown source was `https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra.md`.
- Eric Provencher, [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), read from the author's OpenAI Developers publication. The X entry could not be retrieved; the official full article was available.

The guide recommends making authorization, completion and proportionate verification explicit. The article emphasizes precise discovery descriptions, progressive disclosure and revisiting constraints inherited from earlier models. These are design inputs, not evidence that every reduction in instruction length improves outcomes.

Repository baseline: `8bee7fd90c1256007fdced93959796ae0b370ceb`. The prior repairs were:

- `6841819`: lifecycle reconciliation, terminal-only archives, recoverability, read-only auditing and custom layouts.
- `2fa5bc2`: natural-language invocation, progressive onboarding, bounded clarification and smaller document sets.

Their intended guarantees are retained. The installed local skill already had separate instruction edits; this repository review did not overwrite that installation.

## Rethinking findings

| Problem in the baseline | Consequence | Revision |
| --- | --- | --- |
| Broad 689-character discovery description included document filenames | Ordinary edits could attract governance | 211-character task-based description; preserve explicit/implicit invocation |
| Mandatory brief approval, map approval and prescribed first-turn/question counts | Already authorized work can stop repeatedly | Decide from scope and missing decisions; honor staged review only when requested |
| Entry point repeated lifecycle, team, output and quality procedures | Unneeded instructions load on every invocation | 42-line router, down from 225; task-specific references |
| Generated AGENTS/PROGRESS required broad reading before non-trivial work | Small changes inherit whole-project process | Conditional pointers and project-specific constraints |
| Filename-based conflict priority and event-wide update lists | Stale canonical text can override evidence; duplicated updates | Verify truth against evidence; update only owners of facts that changed |
| Fixed team tiers and coordinator/reviewer defaults | Small tasks acquire staffing and approval overhead | Context-based ownership and proportional delegation/review |
| Terminal classification universally required successful acceptance | Cancelled work could never close correctly | Distinguish successful acceptance from cancellation/rejection/supersession decisions |
| Examples omitted metadata/columns required by the auditor | Copying the scaffold created avoidable warnings | Lean, structurally compatible examples with explicit unknown/evidence boundaries |
| Package tests asserted wording and approval headings | Tests preserved the very workflow constraints under review | Structural package tests plus separate observed model behavior |

The entrypoint and runtime references together decreased from roughly 74,364 to 35,004 characters. This is a text-size measurement, not a measured token, latency, cost or quality improvement.

## Auditor defects reproduced and fixed

New disposable-fixture tests failed against the old auditor for these cases, then passed after the changes:

- The documented `documents.run_registry` mapping was ignored because only `run` was recognized.
- Missing explicit configs/documents and malformed configuration could silently fall back to partial/default checks.
- Only the first task table was inspected, allowing later blocked archive rows to escape detection.
- A TODO table using `Final Status` was recognized and then crashed because its status index was read differently.
- Fenced example tasks were treated as live work.
- Unicode/long task IDs were not matched completely by the next-action check.
- Phase substring comparison treated S1 and S10 as compatible.
- An unknown archive status was not flagged; a configured alias could also classify Blocked as terminal.
- `--output` could overwrite TODO.md while claiming a read-only audit.

The output boundary now rejects project-internal reports and outside hard links to project files. Valid outside reports preserve all project bytes. Custom/legacy run mappings, optional null roles and the original lifecycle fixtures remain supported.

Compatibility changes: explicit missing/invalid inputs now return exit code 2, unsupported malformed tables fail visibly, and output reports must be outside the audited project. These changes prevent silent partial auditing and input overwrites. Existing client entrypoint shims can be mapped explicitly rather than being declared invalid merely for coexisting.

## First revision validation (7038616)

On Windows with bundled Python 3.12:

- Original baseline suite: 14 tests passed. Its coverage did not catch the reproduced defects.
- Revised suite: 27 tests passed, including the existing lifecycle regressions.
- Skill Creator's YAML-aware `quick_validate.py`: passed. Its PyYAML dependency was installed into an isolated validation directory, not added as a ProjectOS runtime dependency.
- ProjectOS package validator: 0 errors; checkout-only warning because the repository folder is named `projectOS` rather than the installed skill name `project-os`.
- Whitespace/diff checks: passed.

Commands for the repository checks:

```bash
python -m unittest discover -s tests -v
python scripts/validate_skill.py .
git diff --check
```

## First revision independent behavior trials

Fresh Astra subagents used the candidate skill in isolated local directories, without the expected result or proposed fixes in their prompts. The parent inspected the generated artifacts.

| Trial | Request and observed result |
| --- | --- |
| Plan and implement | Standard-library word-frequency CLI with two explicit acceptance inputs. Produced executable code and minimal docs, returned the required JSON for repeated words and empty input, and completed 9 local CLI/function checks without a brief/map approval pause. |
| Mixed-state closeout | Existing Done, Cancelled, Blocked and Review tasks with raw evidence and a cancellation decision. Archived only Done/Cancelled, preserved the decision and evidence, retained Blocked/Review and the unfinished stage, and selected a valid independent next action. Its lifecycle audit reported no findings. |
| Planning only | The same small CLI idea with an explicit no-files/no-code request. Returned an actionable plan and acceptance criteria, accurately stated that no tests had run, and left the isolated workspace empty. |

These are observed local smoke trials, not a statistically controlled benchmark. The closeout inputs are synthetic evidence fixtures, not real production runs. The full scenario catalog includes additional cases not claimed as executed here. No comparative speed/cost result or cross-model guarantee is claimed.

## Remaining limits

The auditor understands a bounded Markdown/config schema. It does not validate experiment artifact contents, retention obligations, every prose reference, or semantic acceptance. A clean report therefore cannot authorize deletion or upgrade smoke evidence to formal results.

Package validation similarly cannot prove routing quality. Preserve project-specific constraints and use realistic behavior trials when changing the workflow; do not replace them with more exact-phrase assertions or a universal instruction checklist.

## Second pass: lifecycle continuity

The follow-up review examined the whole lifecycle rather than only shorter prompting. The entrypoint remains 42 lines; advanced transitions and the audit schema are loaded through lifecycle references when relevant.

| Gap | Change |
| --- | --- |
| Creation, adoption and retirement were less explicit than cleanup | Define provenance, draft/adopted boundaries, successor ownership, effective versions and conditional writeback in project entrypoints |
| Confidence, document lifecycle and task execution were mixed | Explain their independence; archived evidence may remain valid, while a completed task can require a later correction |
| Evidence withdrawal did not specify downstream reconciliation | Preserve the original observation and correction; revisit affected claims, stage gates and dependent work without automatically rerunning experiments |
| Reopening and interrupted closeout could erase or duplicate history | Use distinct attempt IDs, preserve old outcomes, compare existing archive rows, finish only missing changes and recover selectively |
| Small combined documents were recommended but not auditable by role | Add path/section mappings, inherited metadata, stable physical line numbers and one cached source revision per file |
| Clean output did not show actual coverage | Reports now list inspected roles/sections/checks and row counts; empty scans are errors and excluded semantics are explicit |
| Dependency/readiness errors and ambiguous next actions were missed | Check missing prerequisites, cycles and readiness against unfinished/cancelled work; support explicit Next Task and warn on ambiguous prose |
| Fresh top-level dates hid old tasks; terminal evidence could be blank | Check row freshness and empty fields, duplicate archive attempts, placeholder outcome evidence and noncurrent mapped owners |
| Ordinary future coding could bypass lifecycle upkeep entirely | Generated project entrypoints conditionally write back changed facts; installing a skill does not imply a background watcher |

These changes add 15 regression cases. The complete suite now has **42 passing tests**; the first 12 new cases included 11 failures against the previous implementation before repairs. Additional positive tests cover valid escaped pipes, section isolation, historical-size isolation and source-revision consistency. Existing custom layouts, implicit/explicit invocation and read-only protections remain covered.

The first advanced recovery trial also exposed a behavioral failure: it correctly retracted bad evidence and repaired the interrupted closeout, but completed an unrelated Ready glossary task during a reconciliation-only request. The skill now explicitly separates queue readiness from execution authorization. This is a correction based on observed behavior, not a new blanket approval gate.

Observed follow-up artifacts:

| Trial | Outcome |
| --- | --- |
| Combined project document | Preserved the four PROJECT.md sections, archived only the completed welcome-note task, retained the blocked connection task, and created a section map. Audit coverage identified one live queue row and two historical rows with no findings. |
| Recovery after evidence withdrawal, first attempt | Preserved the original result and historical acceptance, opened a corrective attempt and repaired the queue; failed the scope boundary by also completing the unrelated glossary task. |
| Same recovery request in a fresh workspace after correction | Kept the glossary task Ready and unexecuted. Preserved one historical T-001 row, removed the interrupted duplicate, created blocked T-001-R2, redirected T-003 to it, and withdrew R-001's formal accuracy claim while retaining the original observation. |

Advanced behavior trials use synthetic local project records. They do not demonstrate experimental validity or performance improvements. Cross-file snapshots are not transactional: coordinate writers and verify the relevant revision before a multi-file transition. The auditor caches repeated roles from the same file but does not replace version control or semantic review.

## Third pass: precision and package readiness

The final refinement pass kept the 42-line entrypoint and focused on incorrect audit outcomes, metadata integrity and maintainability rather than adding workflow ceremonies.

| Reproduced boundary | Correction |
| --- | --- |
| A nested section inherited earlier unrelated sections as its preamble | Inherit only field lines from the document header, independent of selected heading depth |
| A literal heading such as C# lost its final hash | Distinguish literal heading text from spaced Markdown closing hashes |
| A Markdown link's destination looked like another task dependency | Interpret task references from visible labels, not URL/path tokens |
| A trust glossary masked missing classifications in actual run rows | Identify run tables separately and check each table/row, including missing/duplicate IDs and empty trust values |
| Empty archive IDs and missing active stages escaped useful diagnostics | Report these conditions while accepting a completed roadmap with an empty queue |
| Duplicate JSON keys, empty normalized status aliases, and explicit null entrypoints were ambiguous | Reject ambiguous config values and respect deliberate discovery disablement |
| Invalid or duplicate discovery fields, truncated quotes, corrupt UTF-8, or a wrong skill-name prefix could pass or crash package checks | Return concrete package errors, parse basic description blocks, enforce name bounds and match explicit invocation exactly |
| Report I/O failures did not follow the documented exit-code contract | Return exit 2 with a concise diagnostic; clarify CLI help and input failures |

The suite now contains **61 passing tests**, including positive cases guarding against new false alarms. Both Python tools and the new tests were formatted for maintainability; text-file line endings are declared for portable checkouts. Formatting/YAML-aware validation dependencies stayed in isolated development directories and are not runtime dependencies of the skill.

An independent read-only trial used a project with nested sections, a historical snapshot, a proposed stage and an unexecuted evaluation. The evaluator correctly reported RUN_TRUST_MISSING and NO_ACTIVE_STAGE, checked that the result artifact did not exist, and distinguished setup completion from evaluation readiness. It did not implement repairs or run an experiment. The parent compared all five project file hashes before/after and confirmed no input changes.

The package validator deliberately implements the metadata subset used by this package, not arbitrary YAML extensions. A YAML-aware client validator remains appropriate for richer metadata. The observed tests and local trials support these specific behaviors; they are not a proof of correctness for every future project or model.
