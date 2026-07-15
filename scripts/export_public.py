#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

IGNORED = shutil.ignore_patterns(
    ".DS_Store", ".pytest_cache", ".ruff_cache", "__pycache__", "*.pyc"
)


def _replace_tree(staging: Path, destination: Path) -> None:
    backup = destination.with_name(f".{destination.name}.backup")
    if backup.exists():
        shutil.rmtree(backup)
    try:
        if destination.exists():
            destination.rename(backup)
        staging.rename(destination)
    except BaseException:
        if destination.exists():
            shutil.rmtree(destination)
        if backup.exists():
            backup.rename(destination)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def export_public(source: Path, destination: Path) -> int:
    source = source.resolve()
    destination = destination.resolve()
    if destination == source or destination.is_relative_to(source):
        raise ValueError("destination must be outside the source package")
    skills_root = source / "plugins" / "polygres" / "skills"
    skills = sorted(path for path in skills_root.iterdir() if (path / "SKILL.md").is_file())
    if not skills:
        raise ValueError("source package does not contain any skills")

    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.staging-", dir=destination.parent))
    try:
        shutil.copytree(source, staging, dirs_exist_ok=True, ignore=IGNORED)
        discovery_root = staging / "skills"
        if discovery_root.exists():
            shutil.rmtree(discovery_root)
        discovery_root.mkdir()
        for skill in skills:
            shutil.copytree(skill, discovery_root / skill.name, ignore=IGNORED)
        _replace_tree(staging, destination)
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    return len(skills)


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 2:
        print("usage: export_public.py SOURCE_PACKAGE DESTINATION", file=sys.stderr)
        return 2
    try:
        count = export_public(Path(arguments[0]), Path(arguments[1]))
    except (OSError, ValueError) as error:
        print(f"export failed: {error}", file=sys.stderr)
        return 2
    print(f"Exported {count} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
