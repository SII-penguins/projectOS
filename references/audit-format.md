# Auditor Input and Coverage

Use when configuring or interpreting `scripts/audit_project_docs.py`. The auditor is a read-only structural aid. It does not decide which facts are true or authorize lifecycle changes.

## Owners and combined documents

Default filenames are discovered only if present. Explicit mappings must exist. A string maps a whole file; a `path`/`section` object selects exactly one Markdown heading subtree, case-sensitively, outside code fences. The shared preamble is inherited; matching section fields override shared fields. Line numbers in findings remain physical source lines.

Example `projectos.audit.json` for a small project:

```json
{
  "documents": {
    "entrypoint": "AGENTS.md",
    "progress": {"path": "PROJECT.md", "section": "Current state"},
    "todo": {"path": "PROJECT.md", "section": "Active work"},
    "plan": {"path": "PROJECT.md", "section": "Roadmap"},
    "archive": {"path": "PROJECT.md", "section": "History"}
  }
}
```

Use unambiguous headings. Shared metadata consists of field lines in the document header, before its first section and after an optional top-level title. Earlier unrelated sections are never inherited, even when selecting a nested heading. Other section bodies are excluded, so history rows do not become live tasks. Nested subsections belong to their selected parent; literal heading text such as `C#` is preserved.

Supported document roles: `entrypoint`, `progress`, `todo`, `plan`, `run_registry` (legacy alias `run`), `prd`, `frontend`, `backend`, `flow`, `team`, `lessons`, `archive`. `null` disables that default owner. Additional `diagnostics_globs` and `task_archive_globs` extend the default discovery paths. Configured inputs and matched files must remain within the project root.

The `archive` role defaults to `doc/archive/TASKS.md`; additional shards default to `doc/archive/tasks/**/*.md`. A mapped archive is read once, including when a glob matches that same path. Use explicit section mapping when live work and history share a file. Do not duplicate owners just to satisfy the auditor.

## Supported structure

- Metadata uses `Field: value` lines. Lifecycle field meanings are in `references/lifecycle-protocol.md`.
- Task tables use `ID` and `Status` or `Final Status`. Unicode IDs, multiple tables, and escaped pipes are supported. Fenced examples are excluded. An unclosed fence is an error because it can hide real content.
- Active rows can include `Owner`, `Dependencies`, `Next Action`, `Acceptance Gate`, `Evidence`, `Last Touched`. Missing columns are reported for review; their presence does not prove the data is correct.
- Empty owner/action/acceptance fields, invalid/future task dates, and old task dates are review findings. Refreshing a document-level date does not refresh every task or authorize closing an old task.
- Archive rows preserve unique attempt IDs and non-placeholder outcome evidence or a cancellation decision. Reopened attempts use a distinct ID linked to the old outcome; see `references/lifecycle-transitions.md`.
- Each run table has a unique `ID` (or `Run ID`/`Run`) and a `Trust`/`Trust Level` column with non-placeholder values. A separate trust glossary does not validate run rows. Artifact content and scientific validity are not checked.
- A roadmap identifies its current stage. `Next Task: T-002` may disambiguate a prose `Next Action` that mentions several tasks. Multiple references without this field produce a warning, not a guess about which task is next.

## Dependencies

`Dependencies` is interpreted as prerequisites, not merely related work. The auditor recognizes existing task IDs and token-like references such as `T-001`, including Unicode hyphenated IDs. It checks missing referenced tasks, active dependency cycles and Ready/In Progress/Review rows with prerequisites not marked Done/Completed.

Markdown link labels can identify tasks; identifiers embedded only in their URL/path are not additional task dependencies. An empty task/run ID is an error. Duplicate JSON config keys and aliases that normalize to an empty status are rejected rather than silently overriding earlier intent.

These are structural findings. External prerequisites, conditional prose, and project-specific success aliases need direct interpretation. A custom terminal status is not assumed to mean successful completion. Put relationship/history links that are not prerequisites in a separate `Related`/`Reopens` column so they do not become accidental dependencies.

Status arrays `active_task_statuses` and `terminal_task_statuses` extend defaults; the sets must not overlap. The tool never changes task state, archives rows or removes dependencies.

## Report coverage and exit codes

Both Markdown and JSON reports identify inspected owners/sections and checks applied. JSON includes `coverage.documents`, `checks`, and queue/archive row counts. An empty scan returns a `NO_DOCUMENTS` error. A partial layout may be valid, but missing roles mean the corresponding cross-document checks were not performed.

Active work with no active roadmap stage, or a phase absent from the roadmap, produces a review warning. A completed roadmap with an empty queue is valid; the auditor does not invent work to keep a project active.

The report explicitly excludes artifact contents, semantic acceptance, retention and deletion authorization. Check the coverage before claiming an audit passed for a particular purpose.

Use `--format json` for machine-readable output, `--today YYYY-MM-DD` for deterministic freshness checks, and `--fail-on error|warn|none` to choose the finding threshold. Exit 0 means the selected threshold was not exceeded, exit 1 means it was, and exit 2 means invalid input or execution failure. `--fail-on none` does not clear findings.

Reports default to stdout. `--output` must be outside the audited project and cannot alias a project file, including via a hard link. Thresholds accept positive integers: `progress_stale_days`, `todo_stale_days`, `plan_stale_days`, and `max_progress_lines` (nonempty lines of the selected live view).
