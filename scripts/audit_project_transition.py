#!/usr/bin/env python3
"""Read-only before/after checks; stdout is the only output destination.

capture ROOT saves the actual working inputs when its stdout is retained by the
caller. compare ROOT --before SNAPSHOT checks obligations; guard checks that the
captured inputs are unchanged before an edit. Snapshots are not authorization.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys

import audit_project_docs as audit

SCHEMA = "projectos-transition-v1"
CAPTURE_ROLES = {"progress", "todo", "plan", "archive"}
EXIT_COLUMNS = ("Exit ID", "Requirement", "Status", "Tasks", "Decision", "Owner", "Revisit")
OPEN_EXITS = {"open", "pending", "blocked", "review"}
EXIT_STATES = OPEN_EXITS | {"satisfied", "deferred", "transferred", "cancelled", "superseded"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exits_from(text, path):
    records, unsupported = [], []
    for heads, rows in audit.tables(text):
        if audit.idx(heads, "Exit ID") is None:
            continue
        columns = {name: audit.idx(heads, name) for name in EXIT_COLUMNS}
        missing = [name for name, col in columns.items() if col is None]
        if missing:
            unsupported.append({"path": path, "missing_columns": missing})
            continue
        for line, cells in rows:
            item = {name: cells[col].strip() for name, col in columns.items()}
            item.update(path=path, line=line)
            records.append(item)
    return records, unsupported


def capture(root, config_arg=None):
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be a directory")
    cfg, cp = audit.config(root, config_arg)
    docs = audit.discover(root, cfg, roles=CAPTURE_ROLES)
    paths = {p for p, _ in docs.values()}
    if cp:
        paths.add(cp)
    hashes = {audit.rel(p, root): file_hash(p) for p in paths}
    # Reject a normal concurrent edit instead of assembling mixed versions.
    cfg_again, cp_again = audit.config(root, config_arg)
    if cfg_again != cfg or cp_again != cp or audit.discover(root, cfg, roles=CAPTURE_ROLES) != docs:
        raise ValueError("Inputs changed during capture; reconcile concurrent writer")
    if any(file_hash(root / name) != value for name, value in hashes.items()):
        raise ValueError("Inputs changed during capture; retry only after coordination")
    roles = {}
    for key, (path, text) in docs.items():
        relative = audit.rel(path, root)
        # Absolute paths in auto-discovered role names are not stable identifiers.
        role = "archive:" + relative if key.startswith("archive:") else key
        if key.startswith("diag:"):
            role = "diag:" + relative
        roles[role] = {"path": relative, "text": text}
    result = {"schema": SCHEMA, "project_root": str(root), "config": cfg,
              "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
              "files": hashes, "roles": roles,
              "limits": ["not authorization", "not artifact verification",
                         "not an atomic filesystem snapshot"]}
    result["digest"] = digest(result)
    return result


def load_snapshot(path):
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=audit.unique_json_object)
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("Unsupported snapshot schema")
    expected = data.get("digest")
    unsigned = {k: v for k, v in data.items() if k != "digest"}
    if expected != digest(unsigned):
        raise ValueError("Snapshot digest mismatch; do not manufacture a replacement baseline")
    if not isinstance(data.get("roles"), dict) or not isinstance(data.get("files"), dict):
        raise ValueError("Invalid snapshot fields")
    return data


def task_index(snapshot):
    records, duplicates = {}, []
    for role, view in snapshot["roles"].items():
        if role != "todo" and not audit.is_archive(role):
            continue
        for rec in audit.task_records(view["path"], view["text"], snapshot["config"]):
            rec["location"] = "active" if role == "todo" else "archive"
            if rec["id"] in records:
                duplicates.append(rec["id"])
            records[rec["id"]] = rec
    return records, duplicates


def compare(before, after):
    if before["project_root"] != after["project_root"]:
        raise ValueError("Baseline belongs to a different root/worktree")
    out, gaps = [], []

    def add(code, message, severity="ERROR", item=None):
        item = item or {}
        out.append(audit.finding(severity, code, item.get("path", "."), message, item.get("line")))

    roles = after["roles"]
    active = audit.ACTIVE | {audit.norm(x) for x in after["config"].get("active_task_statuses", [])}
    terminal = audit.TERMINAL | {audit.norm(x) for x in after["config"].get("terminal_task_statuses", [])}
    if before["config"] != after["config"]:
        add("CONFIG_CHANGED_REVIEW", "Audit mapping/status semantics changed; review affected coverage.", "WARN")
    for label, snapshot in (("before", before), ("after", after)):
        todo = snapshot["roles"].get("todo")
        if not todo or not list(audit.task_tables(todo["text"])):
            gaps.append(f"{label}: no supported task table")
    old, old_dupes = task_index(before)
    new, new_dupes = task_index(after)
    for label, records in (("before", old), ("after", new)):
        if any(r["location"] == "active" and r["acceptance"] is None for r in records.values()):
            gaps.append(f"{label}: missing acceptance column for active task rows")
    resolved_duplicates = []
    for task in sorted(set(new_dupes)):
        add("TRANSITION_TASK_DUPLICATE", f"Task {task} appears more than once after the transition; destination is ambiguous.")
    for task in sorted(set(old_dupes) - set(new_dupes)):
        versions = [rec for role, view in before["roles"].items()
                    if role == "todo" or audit.is_archive(role)
                    for rec in audit.task_records(view["path"], view["text"], before["config"])
                    if rec["id"] == task]
        outcomes = {(rec["status"], rec["evidence"]) for rec in versions}
        gates = {rec["acceptance"] for rec in versions if rec["acceptance"] is not None}
        if len(outcomes) == 1 and len(gates) <= 1 and all(rec["status"] in terminal for rec in versions):
            resolved_duplicates.append(task)
        else:
            add("BASELINE_DUPLICATE_REVIEW", f"Task {task} had conflicting/unfinished duplicate records before reconciliation; verify which obligations survive.", "WARN")
    for tid, prior in old.items():
        current = new.get(tid)
        if current is None:
            add("TASK_DISAPPEARED" if prior["location"] == "active" else "HISTORY_DISAPPEARED",
                f"{tid} has no retained destination; inspect completion, transfer or cancellation.", item=prior)
            continue
        if current.get("object_kind", "task") != prior.get("object_kind", "task"):
            add("OBJECT_KIND_CHANGED", f"{tid} object kind changed; a task obligation cannot be reclassified as a run outcome.", item=current)
        if prior["location"] == "archive":
            if (current["status"], current["evidence"], current["location"]) != (
                    prior["status"], prior["evidence"], prior["location"]):
                add("HISTORY_CHANGED_REVIEW", f"{tid} prior outcome changed; preserve correction provenance.", "WARN", current)
        elif prior["acceptance"] is not None:
            # A terminal archive may omit the old gate; the captured before-state
            # retains it. An active row may not silently weaken/drop it.
            if current["location"] == "active" and current["acceptance"] != prior["acceptance"]:
                add("ACCEPTANCE_CHANGED_REVIEW", f"{tid} acceptance changed; verify scope and governing decision.", "WARN", current)
        if current["location"] == "archive" and not audit.record_terminal(current, terminal):
            add("NONTERMINAL_ARCHIVED", f"{tid} is still open or its terminal state is unsupported.", item=current)
        if prior["location"] == "active" and audit.record_terminal(current, terminal):
            if current["evidence_state"] != "present_unverified":
                add("TERMINAL_OUTCOME_UNVERIFIED", f"{tid} outcome/decision field is {current['evidence_state']}.", item=current)
            if current["location"] == "active":
                add("TERMINAL_DESTINATION_PENDING", f"{tid} is terminal but remains in the active queue.", "WARN", current)
    for tid, current in new.items():
        if tid not in old and current["location"] == "archive" and current.get("object_kind", "task") != "task":
            if not audit.record_terminal(current, terminal):
                add("NONTERMINAL_ARCHIVED", f"{tid} has an unsupported object/outcome or a still-active attempt.", item=current)
    exit_sets = []
    for label, snapshot in (("before", before), ("after", after)):
        plan = snapshot["roles"].get("plan")
        rows, unsupported = exits_from(plan["text"], plan["path"]) if plan else ([], [])
        has_table = plan and any(audit.idx(h, "Exit ID") is not None for h, _ in audit.tables(plan["text"]))
        if not has_table:
            gaps.append(f"{label}: no explicit exit-obligation table; free-text stage exits not checked")
        if unsupported:
            gaps.append(f"{label}: unsupported exit columns: {unsupported}")
        mapped = {}
        for row in rows:
            eid = row["Exit ID"].strip("` ")
            if not eid or eid in mapped:
                add("EXIT_ID_INVALID", f"{label}: missing or duplicate exit ID {eid!r}.", item=row)
            mapped[eid] = row
        exit_sets.append(mapped)
    old_exits, new_exits = exit_sets
    for eid, prior in old_exits.items():
        current = new_exits.get(eid)
        if current is None:
            add("EXIT_DISAPPEARED", f"Exit {eid} has no retained disposition.", item=prior)
        elif current["Requirement"] != prior["Requirement"]:
            add("EXIT_REQUIREMENT_CHANGED_REVIEW", f"Exit {eid} requirement changed; verify authority.", "WARN", current)
        if current and audit.norm(prior["Status"]) != audit.norm(current["Status"]):
            add("EXIT_STATUS_CHANGED_REVIEW", f"Exit {eid} changed state; check evidence and decision scope.", "WARN", current)
    for eid, row in new_exits.items():
        status = audit.norm(row["Status"])
        refs = audit.task_references(row["Tasks"], set(new))
        if status not in EXIT_STATES:
            add("EXIT_STATUS_UNSUPPORTED", f"Exit {eid} has unsupported state {status!r}.", item=row)
        elif status in OPEN_EXITS:
            if not refs:
                add("EXIT_UNCOVERED", f"Open exit {eid} has no carrying task.", item=row)
            for tid in refs:
                rec = new.get(tid)
                if not rec or rec["location"] != "active" or rec["status"] not in active or rec.get("object_kind", "task") != "task":
                    add("EXIT_TASK_NOT_ACTIVE", f"Open exit {eid} refers to non-active task {tid}.", item=row)
        else:
            if audit.norm(row["Decision"]) in audit.EMPTY_EVIDENCE:
                add("EXIT_DISPOSITION_MISSING", f"Exit {eid} needs an evidence/decision reference.", item=row)
            if status in {"deferred", "transferred"} and (not row["Owner"] or not row["Revisit"]):
                add("EXIT_TRACKING_MISSING", f"Exit {eid} needs owner and revisit event.", item=row)
    for role, view in roles.items():
        if role == "progress":
            out.extend(audit.duplicate_current_fields(Path(view["path"]), view["text"], Path(".")))
    changed = sorted(p for p in set(before["files"]) | set(after["files"])
                     if before["files"].get(p) != after["files"].get(p))
    has_errors = any(x["severity"] == "ERROR" for x in out)
    return {"schema": SCHEMA, "read_only": True, "project_root": after["project_root"],
            "baseline_digest": before["digest"], "current_digest": after["digest"],
            "changed_files": changed, "findings": out,
            "resolved_baseline_duplicates": resolved_duplicates,
            "status": "findings" if has_errors else "review_required" if out else "partial" if gaps else "checked",
            "coverage": {"task_destinations": not any("task table" in x for x in gaps),
                         "acceptance_changes": not any("acceptance column" in x for x in gaps),
                         "explicit_exits": not any("exit" in x for x in gaps), "gaps": gaps,
                         "not_checked": ["free-text semantics", "approval authenticity", "artifact contents",
                                         "evidence retraction consumers without structured bindings",
                                         "external concurrent edits outside captured owners"]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("capture", "compare", "guard"))
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--config")
    parser.add_argument("--before", type=Path)
    args = parser.parse_args()
    try:
        current = capture(args.project_root, args.config)
        if args.command == "capture":
            result, code = current, 0
        else:
            if not args.before:
                raise ValueError("--before is required; missing baseline is not a pass")
            before = load_snapshot(args.before)
            if before["project_root"] != current["project_root"]:
                raise ValueError("Baseline belongs to a different root/worktree")
            if args.command == "guard":
                changed = before["files"] != current["files"] or before["config"] != current["config"]
                result = {"read_only": True, "status": "changed" if changed else "unchanged",
                          "limits": "A point-in-time check, not a lock or permission to overwrite."}
                code = 1 if changed else 0
            else:
                result = compare(before, current)
                code = 1 if result["findings"] else 3 if result["status"] == "partial" else 0
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return code
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({"read_only": True, "status": "unchecked", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
