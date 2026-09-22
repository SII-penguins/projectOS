#!/usr/bin/env python3
"""Validate the ProjectOS Agent Skill package with the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REFERENCE_RE = re.compile(
    r"`((?:references|scripts|agents)/[A-Za-z0-9_.\-/]+)`|\]\(((?:references|scripts|agents)/[^\s)#]+)(?:#[^)]*)?\)"
)


@dataclass(frozen=True)
class Finding:
    severity: str
    message: str


def parse_scalar(value: str) -> str:
    """Parse the plain/quoted string subset used by this package's YAML fields."""
    value = value.strip()
    if value.startswith('"'):
        try:
            parsed, end = json.JSONDecoder().raw_decode(value)
        except ValueError as exc:
            raise ValueError(
                "Invalid quoted string; use a complete JSON-compatible YAML string"
            ) from exc
        if value[end:].strip() and not value[end:].lstrip().startswith("#"):
            raise ValueError("Unexpected content after quoted string")
        return parsed
    if value.startswith("'"):
        match = re.fullmatch(r"'((?:[^']|'')*)'(?:\s+#.*)?", value)
        if not match:
            raise ValueError("Invalid single-quoted YAML string")
        return match[1].replace("''", "'")
    value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
    if value and (
        value[0] in "[{}]&*!|>"
        or value.lower() in {"true", "false", "null", "~", "yes", "no", "on", "off"}
        or re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value)
        or re.search(r":\s", value)
    ):
        raise ValueError("Expected a string scalar; quote values that resemble YAML data")
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
    index = 1
    while index < end:
        raw = lines[index]
        index += 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw != raw.lstrip():
            continue
        if not re.match(r"^[A-Za-z_][\w-]*\s*:", raw):
            raise ValueError("Malformed top-level frontmatter field")
        key, value = raw.split(":", 1)
        key, value = key.strip(), value.strip()
        if key in metadata:
            raise ValueError(f"Duplicate frontmatter field: {key}")
        if key not in {"name", "description"}:
            # Optional metadata is preserved, not interpreted as a full YAML schema.
            metadata[key] = value
            continue
        if re.fullmatch(r"[>|][-+]?", value):
            block = []
            while index < end and (
                not lines[index].strip() or lines[index] != lines[index].lstrip()
            ):
                block.append(lines[index])
                index += 1
            content = textwrap.dedent("\n".join(block)).strip("\n")
            if value[0] == ">":
                content = re.sub(r"(?<=[^\n])\n(?=[^\n])", " ", content)
            metadata[key] = content
        else:
            metadata[key] = parse_scalar(value)
    return metadata, "\n".join(lines[end + 1 :])


def validate(root: Path) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []

    def read_text(path: Path) -> str | None:
        if not path.resolve().is_relative_to(root):
            findings.append(Finding("ERROR", f"Resource escapes skill: {path.relative_to(root)}"))
            return None
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append(
                Finding("ERROR", f"Cannot read UTF-8 resource {path.relative_to(root)}: {exc}")
            )
            return None

    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        return [Finding("ERROR", f"Missing required file: {skill_path}")]

    text = read_text(skill_path)
    if text is None:
        return findings
    try:
        metadata, body = parse_frontmatter(text)
    except ValueError as exc:
        return [Finding("ERROR", str(exc))]

    name = metadata.get("name", "").strip()
    description = metadata.get("description", "").strip()
    if not name:
        findings.append(Finding("ERROR", "Frontmatter is missing required field: name"))
    elif not NAME_RE.fullmatch(name):
        findings.append(Finding("ERROR", f"Invalid skill name {name!r}; use lowercase kebab-case"))
    elif len(name) > 64:
        findings.append(Finding("ERROR", "Skill name exceeds 64 characters"))
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
        findings.append(
            Finding("ERROR", f"Description is {len(description)} characters; maximum is 1024")
        )
    elif "<" in description or ">" in description:
        findings.append(Finding("ERROR", "Description cannot contain angle brackets"))

    line_count = len(text.splitlines())
    if line_count > 500:
        findings.append(
            Finding("ERROR", f"SKILL.md has {line_count} lines; keep it at or below 500")
        )
    elif line_count > 350:
        findings.append(
            Finding("WARN", f"SKILL.md has {line_count} lines; use more progressive disclosure")
        )

    # Check resources, not prose slogans. Model behavior needs independent evaluation.
    instruction_files = [skill_path, *(root / "references").glob("*.md")]
    for source in instruction_files:
        source_text = text if source == skill_path else read_text(source)
        if source_text is None:
            continue
        for match in REFERENCE_RE.finditer(source_text):
            relative = match[1] or match[2]
            target = (root / relative).resolve()
            if not target.is_relative_to(root.resolve()):
                findings.append(Finding("ERROR", f"Reference escapes skill: {relative}"))
            elif not target.is_file():
                findings.append(Finding("ERROR", f"Referenced path does not exist: {relative}"))

    required = {
        "references/onboarding-and-invocation.md",
        "references/evaluation-scenarios.md",
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
        openai_text = read_text(openai_path) or ""
        prompts = re.findall(r"^\s*default_prompt:\s*(.+)$", openai_text, re.M)
        try:
            valid_prompt = len(prompts) == 1 and re.search(
                r"\$" + re.escape(name) + r"(?![\w-])", parse_scalar(prompts[0])
            )
        except ValueError:
            valid_prompt = False
        if not valid_prompt:
            findings.append(
                Finding("ERROR", "OpenAI default prompt must unambiguously name the exact skill")
            )
        policies = re.findall(r"^\s*allow_implicit_invocation:\s*(\S+)", openai_text, re.M)
        if len(policies) > 1 or (policies and policies[0] not in {"true", "false"}):
            findings.append(Finding("ERROR", "allow_implicit_invocation must be a boolean"))
    else:
        findings.append(Finding("WARN", "agents/openai.yaml is missing"))

    for script in (root / "scripts").glob("*.py"):
        script_text = read_text(script)
        if script_text is None:
            continue
        try:
            compile(script_text, str(script), "exec")
        except SyntaxError as exc:
            findings.append(Finding("ERROR", f"Script has a syntax error: {exc}"))

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
