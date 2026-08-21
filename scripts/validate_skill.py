#!/usr/bin/env python3
"""Validate the ProjectOS Agent Skill package with the Python standard library."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REFERENCE_RE = re.compile(r"`((?:references|scripts|agents)/[A-Za-z0-9_.\-/]+)`")


@dataclass(frozen=True)
class Finding:
    severity: str
    message: str


def parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must begin with YAML frontmatter delimited by ---")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as exc:
        raise ValueError("SKILL.md frontmatter has no closing ---") from exc

    metadata: dict[str, str] = {}
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#") or ":" not in raw:
            continue
        if raw != raw.lstrip():
            continue
        key, value = raw.split(":", 1)
        metadata[key.strip()] = parse_scalar(value)
    return metadata, "\n".join(lines[end + 1 :])


def validate(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        return [Finding("ERROR", f"Missing required file: {skill_path}")]

    text = skill_path.read_text(encoding="utf-8")
    try:
        metadata, body = parse_frontmatter(text)
    except ValueError as exc:
        return [Finding("ERROR", str(exc))]

    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not name:
        findings.append(Finding("ERROR", "Frontmatter is missing required field: name"))
    elif not NAME_RE.fullmatch(name):
        findings.append(Finding("ERROR", f"Invalid skill name {name!r}; use lowercase kebab-case"))
    if name and root.name != name:
        findings.append(
            Finding(
                "WARN",
                f"Skill directory {root.name!r} differs from frontmatter name {name!r}; package releases should use a `{name}/` wrapper.",
            )
        )

    if not description:
        findings.append(Finding("ERROR", "Frontmatter is missing required field: description"))
    elif len(description) > 1024:
        findings.append(Finding("ERROR", f"Description is {len(description)} characters; maximum is 1024"))
    elif len(description) < 80:
        findings.append(Finding("WARN", "Description may be too short for reliable invocation"))

    line_count = len(text.splitlines())
    if line_count > 500:
        findings.append(Finding("ERROR", f"SKILL.md has {line_count} lines; keep it at or below 500"))
    elif line_count > 350:
        findings.append(Finding("WARN", f"SKILL.md has {line_count} lines; use more progressive disclosure"))

    for invariant in (
        "One fact, one canonical owner",
        "Audit before cleanup",
        "Promote before removing",
        "safe-deletion",
    ):
        if invariant.lower() not in body.lower():
            findings.append(Finding("ERROR", f"Missing lifecycle invariant: {invariant}"))

    for relative in sorted(set(REFERENCE_RE.findall(text))):
        if not (root / relative).exists():
            findings.append(Finding("ERROR", f"Referenced path does not exist: {relative}"))

    required = {
        "references/interrogation-checklist.md",
        "references/lifecycle-protocol.md",
        "references/document-blueprints.md",
        "references/team-blueprint.md",
        "references/hard-rules.md",
        "references/example-output-skeleton.md",
        "scripts/audit_project_docs.py",
    }
    for relative in sorted(required):
        if not (root / relative).is_file():
            findings.append(Finding("ERROR", f"Missing required ProjectOS resource: {relative}"))

    openai_path = root / "agents" / "openai.yaml"
    if openai_path.is_file():
        openai_text = openai_path.read_text(encoding="utf-8")
        if "allow_implicit_invocation: true" not in openai_text:
            findings.append(Finding("WARN", "OpenAI config does not enable implicit invocation"))
        if "$project-os" not in openai_text and "ProjectOS" not in openai_text:
            findings.append(Finding("WARN", "OpenAI default prompt does not name ProjectOS"))
    else:
        findings.append(Finding("WARN", "agents/openai.yaml is missing"))

    try:
        compile(
            (root / "scripts" / "audit_project_docs.py").read_text(encoding="utf-8"),
            "audit_project_docs.py",
            "exec",
        )
    except SyntaxError as exc:
        findings.append(Finding("ERROR", f"Audit script has a syntax error: {exc}"))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "skill_dir",
        nargs="?",
        default=str(Path(__file__).resolve().parents[1]),
        help="Path to the skill directory",
    )
    args = parser.parse_args()
    root = Path(args.skill_dir).resolve()
    findings = validate(root)
    for finding in findings:
        print(f"[{finding.severity}] {finding.message}")
    errors = sum(finding.severity == "ERROR" for finding in findings)
    warnings = sum(finding.severity == "WARN" for finding in findings)
    print(f"Validated {root}: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
