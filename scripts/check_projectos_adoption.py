#!/usr/bin/env python3
"""Read-only static instruction-discovery preview, not proof of host ingestion.

Explicit project root/cwd avoid guessing worktree boundaries. Supply --global-dir
only when that actual host instruction directory is known. This script does not
read configuration, session stores or transcripts, and never changes them.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def inspect(root, cwd, global_dir=None, limit=32768, fallback=()):
    root, cwd = root.resolve(strict=True), cwd.resolve(strict=True)
    if not cwd.is_relative_to(root) or not root.is_dir() or not cwd.is_dir():
        raise ValueError("cwd must be inside the explicit project root")
    if limit < 1:
        raise ValueError("Instruction byte limit must be positive")
    if any(Path(x).name != x or x in {".", ".."} for x in fallback):
        raise ValueError("Fallback names must be plain filenames")
    directories = []
    if global_dir is not None:
        directories.append(global_dir.resolve(strict=True))
    cursor = root
    directories.append(cursor)
    for part in cwd.relative_to(root).parts:
        cursor /= part
        directories.append(cursor)
    selected, shadowed, remaining = [], [], limit
    for directory in dict.fromkeys(directories):
        found = None
        for name in ("AGENTS.override.md", "AGENTS.md", *fallback):
            path = directory / name
            if not path.is_file():
                continue
            content = path.read_bytes()
            if not content.strip():
                continue
            if found is not None:
                shadowed.append(str(path))
                continue
            found = path
            taken = min(remaining, len(content))
            selected.append({"path": str(path), "bytes": len(content), "within_limit_bytes": taken,
                             "truncated_or_omitted": taken < len(content),
                             "sha256": hashlib.sha256(content).hexdigest(),
                             "resolved_path": str(path.resolve())})
            remaining -= taken
    return {"read_only": True, "status": "static_preview", "project_root": str(root),
            "cwd": str(cwd), "selected": selected, "shadowed": shadowed,
            "assumed_limit_bytes": limit,
            "not_verified": ["actual host project root/configuration/fallback policy",
                             "instruction ingestion in a running or fresh session",
                             "semantic conflicts or sufficiency of writeback rules",
                             "global instructions" if global_dir is None else "other host-injected instructions"]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project_root", type=Path)
    ap.add_argument("--cwd", type=Path, required=True)
    ap.add_argument("--global-dir", type=Path)
    ap.add_argument("--limit", type=int, default=32768)
    ap.add_argument("--fallback", action="append", default=[])
    args = ap.parse_args()
    try:
        result = inspect(args.project_root, args.cwd, args.global_dir, args.limit, args.fallback)
    except (ValueError, OSError) as exc:
        print(json.dumps({"read_only": True, "status": "unchecked", "error": str(exc)}))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
