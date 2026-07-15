#!/usr/bin/env python3
from __future__ import annotations

import difflib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REFERENCE = re.compile(r"`(references/[^`]+\.md)`")
FORBIDDEN_PLACEHOLDERS = ("TO" + "DO", "FIX" + "ME", "[TO" + "DO:")


class ValidationFailure(ValueError):
    pass


@dataclass(frozen=True)
class SkillMetadata:
    name: str
    description: str
    root: Path


def _parse_frontmatter(skill_file: Path) -> SkillMetadata:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValidationFailure(f"{skill_file}: frontmatter must start with ---")
    try:
        closing = lines.index("---", 1)
    except ValueError as error:
        raise ValidationFailure(f"{skill_file}: frontmatter is not closed") from error

    values: dict[str, str] = {}
    for line in lines[1:closing]:
        if ":" not in line:
            raise ValidationFailure(f"{skill_file}: malformed frontmatter line {line!r}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    if list(values) != ["name", "description"] or not all(values.values()):
        raise ValidationFailure(f"{skill_file}: frontmatter must contain only name and description")

    name = values["name"]
    if not SKILL_NAME.fullmatch(name):
        raise ValidationFailure(f"{skill_file}: invalid skill name {name!r}")
    if skill_file.parent.name != name:
        raise ValidationFailure(f"{skill_file}: directory must match frontmatter name {name!r}")
    if len(lines) >= 500:
        raise ValidationFailure(f"{skill_file}: SKILL.md must stay below 500 lines")
    return SkillMetadata(name=name, description=values["description"], root=skill_file.parent)


def _validate_references(metadata: SkillMetadata) -> None:
    skill_file = metadata.root / "SKILL.md"
    skill_text = skill_file.read_text(encoding="utf-8")
    root = metadata.root.resolve()
    for relative in REFERENCE.findall(skill_text):
        candidate = (metadata.root / relative).resolve()
        if not candidate.is_relative_to(root):
            raise ValidationFailure(
                f"{skill_file}: reference escapes the skill directory: {relative}"
            )
        if not candidate.is_file():
            raise ValidationFailure(f"{skill_file}: reference does not exist: {relative}")

    for reference in (metadata.root / "references").glob("*.md"):
        lines = reference.read_text(encoding="utf-8").splitlines()
        if len(lines) > 100 and "## Contents" not in lines[:20]:
            raise ValidationFailure(
                f"{reference}: references over 100 lines require a Contents section"
            )


def _validate_skill_files(metadata: SkillMetadata) -> None:
    if not (metadata.root / "agents" / "openai.yaml").is_file():
        raise ValidationFailure(f"{metadata.root}: missing agents/openai.yaml")
    for path in metadata.root.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".py", ".yaml", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        for placeholder in FORBIDDEN_PLACEHOLDERS:
            if placeholder in text:
                raise ValidationFailure(f"{path}: contains forbidden placeholder {placeholder}")
        if "\N{EM DASH}" in text:
            raise ValidationFailure(f"{path}: contains an em dash")


def _validate_descriptions(skills: list[SkillMetadata]) -> None:
    for index, left in enumerate(skills):
        for right in skills[index + 1 :]:
            similarity = difflib.SequenceMatcher(
                None, left.description.casefold(), right.description.casefold()
            ).ratio()
            if similarity >= 0.9:
                raise ValidationFailure(
                    f"{left.root} and {right.root}: skill descriptions are too similar "
                    f"({similarity:.2f})"
                )


def _validate_manifests(package_root: Path, plugin_root: Path) -> None:
    codex = json.loads((plugin_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    claude = json.loads(
        (plugin_root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    marketplace = json.loads(
        (package_root / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
    )
    if codex.get("name") != "polygres" or claude.get("name") != "polygres":
        raise ValidationFailure("plugin manifests must use the name polygres")
    if codex.get("version") != claude.get("version"):
        raise ValidationFailure("Codex and Claude plugin versions must match")
    entries = marketplace.get("plugins", [])
    if len(entries) != 1 or entries[0].get("version") != codex.get("version"):
        raise ValidationFailure("marketplace and plugin versions must match")
    skills_path = (plugin_root / codex.get("skills", "")).resolve()
    if not skills_path.is_relative_to(plugin_root.resolve()) or not skills_path.is_dir():
        raise ValidationFailure("Codex manifest skills path must stay inside the plugin")


def validate_package(package_root: Path) -> list[SkillMetadata]:
    package_root = package_root.resolve()
    plugin_root = package_root / "plugins" / "polygres"
    skills_root = plugin_root / "skills"
    if not skills_root.is_dir():
        raise ValidationFailure(f"{skills_root}: plugin skills directory does not exist")

    skills = [
        _parse_frontmatter(path)
        for path in sorted(skills_root.glob("*/SKILL.md"), key=lambda item: item.parent.name)
    ]
    if not skills:
        raise ValidationFailure(f"{skills_root}: no skills found")
    for metadata in skills:
        _validate_references(metadata)
        _validate_skill_files(metadata)
    _validate_descriptions(skills)
    _validate_manifests(package_root, plugin_root)
    return skills


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("usage: validate_package.py PACKAGE_ROOT", file=sys.stderr)
        return 2
    try:
        skills = validate_package(Path(arguments[0]))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(skills)} skills in the Polygres plugin.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
