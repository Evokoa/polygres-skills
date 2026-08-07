#!/usr/bin/env python3
"""Manage and verify the Polygres skills release version and payload identity."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from typing import Any

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
VERSION_PATTERN = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")
TAG_PREFIX = "polygres-skills-v"
IGNORED_PARTS = {".pytest_cache", ".ruff_cache", "__pycache__"}


class ReleaseValidationError(ValueError):
    pass


def parse_version(value: str) -> tuple[int, int, int]:
    match = VERSION_PATTERN.fullmatch(value)
    if match is None:
        raise ReleaseValidationError("skills version must use the exact X.Y.Z SemVer form")
    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def canonical_version(package_root: Path = PACKAGE_ROOT) -> str:
    value = (package_root / "VERSION").read_text(encoding="utf-8").strip()
    parse_version(value)
    return value


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReleaseValidationError(f"{path}: expected a JSON object")
    return value


def manifest_versions(package_root: Path = PACKAGE_ROOT) -> dict[str, str]:
    plugin_root = package_root / "plugins" / "polygres"
    codex = _read_json(plugin_root / ".codex-plugin" / "plugin.json")
    claude = _read_json(plugin_root / ".claude-plugin" / "plugin.json")
    marketplace = _read_json(package_root / ".claude-plugin" / "marketplace.json")
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
        raise ReleaseValidationError("Claude marketplace must contain exactly one plugin entry")
    versions = {
        "VERSION": canonical_version(package_root),
        "Codex plugin": str(codex.get("version", "")),
        "Claude plugin": str(claude.get("version", "")),
        "Claude marketplace": str(entries[0].get("version", "")),
    }
    for label, value in versions.items():
        try:
            parse_version(value)
        except ReleaseValidationError as error:
            raise ReleaseValidationError(f"{label}: {error}") from error
    return versions


def tag_version(tag: str) -> str:
    if not tag.startswith(TAG_PREFIX):
        raise ReleaseValidationError(f"release tag must use the exact {TAG_PREFIX}X.Y.Z form")
    value = tag.removeprefix(TAG_PREFIX)
    try:
        parse_version(value)
    except ReleaseValidationError as error:
        raise ReleaseValidationError(
            f"release tag must use the exact {TAG_PREFIX}X.Y.Z form"
        ) from error
    return value


def _included_file(path: Path) -> bool:
    return path.is_file() and not IGNORED_PARTS.intersection(path.parts) and path.suffix != ".pyc"


def release_payload(package_root: Path = PACKAGE_ROOT) -> Iterator[tuple[str, bytes]]:
    roots = (
        package_root / ".agents" / "plugins" / "marketplace.json",
        package_root / ".claude-plugin" / "marketplace.json",
        package_root / "README.md",
        package_root / "LICENSE",
    )
    for path in roots:
        if not path.is_file():
            raise ReleaseValidationError(f"release payload file is missing: {path}")
        yield path.relative_to(package_root).as_posix(), path.read_bytes()

    plugin_root = package_root / "plugins" / "polygres"
    for path in sorted(plugin_root.rglob("*")):
        if _included_file(path):
            yield path.relative_to(package_root).as_posix(), path.read_bytes()

    skills_root = plugin_root / "skills"
    for path in sorted(skills_root.rglob("*")):
        if _included_file(path):
            relative = path.relative_to(skills_root)
            yield (Path("skills") / relative).as_posix(), path.read_bytes()


def content_digest(package_root: Path = PACKAGE_ROOT) -> str:
    digest = hashlib.sha256()
    for relative, content in release_payload(package_root):
        encoded_path = relative.encode("utf-8")
        digest.update(len(encoded_path).to_bytes(8, "big"))
        digest.update(encoded_path)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return f"sha256:{digest.hexdigest()}"


def _require_string(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        raise ReleaseValidationError(f"release record field {key!r} must be a non-empty string")
    return value


def validate_release_record(package_root: Path = PACKAGE_ROOT) -> dict[str, Any]:
    version = canonical_version(package_root)
    path = package_root / "releases" / f"{version}.json"
    record = _read_json(path)
    allowed_fields = {
        "$schema",
        "version",
        "release_date",
        "compatibility",
        "content_digest",
        "installation_channels_verified",
        "behavioral_evaluations",
        "known_limitations",
    }
    unexpected = set(record) - allowed_fields
    if unexpected:
        raise ReleaseValidationError(
            f"release record contains unsupported fields: {sorted(unexpected)}"
        )
    if record.get("$schema") != "./schema.json":
        raise ReleaseValidationError("release record must reference ./schema.json")
    if _require_string(record, "version") != version:
        raise ReleaseValidationError("release record version does not match VERSION")
    try:
        date.fromisoformat(_require_string(record, "release_date"))
    except ValueError as error:
        raise ReleaseValidationError("release record release_date must use YYYY-MM-DD") from error
    if _require_string(record, "content_digest") != content_digest(package_root):
        raise ReleaseValidationError("release record content digest does not match the payload")

    compatibility = record.get("compatibility")
    if not isinstance(compatibility, dict):
        raise ReleaseValidationError("release record compatibility must be an object")
    for package_name in ("polygres_cli", "polygres_sdk"):
        package = compatibility.get(package_name)
        if not isinstance(package, dict):
            raise ReleaseValidationError(f"release compatibility is missing {package_name}")
        minimum = _require_string(package, "minimum_supported")
        maximum = _require_string(package, "maximum_tested")
        if parse_version(maximum) < parse_version(minimum):
            raise ReleaseValidationError(
                f"{package_name} maximum_tested cannot be below minimum_supported"
            )
    for tool_name in ("codex", "claude_code", "skills_cli"):
        tool = compatibility.get(tool_name)
        if not isinstance(tool, dict) or "tested" not in tool:
            raise ReleaseValidationError(f"release compatibility is missing {tool_name}.tested")
        if tool["tested"] is not None and (
            not isinstance(tool["tested"], str) or not tool["tested"]
        ):
            raise ReleaseValidationError(f"{tool_name}.tested must be a non-empty string or null")
    for key in (
        "installation_channels_verified",
        "behavioral_evaluations",
        "known_limitations",
    ):
        values = record.get(key)
        if not isinstance(values, list):
            raise ReleaseValidationError(f"release record field {key!r} must be an array")
        if any(not isinstance(value, str) or not value for value in values):
            raise ReleaseValidationError(
                f"release record field {key!r} must contain non-empty strings"
            )
        if key == "installation_channels_verified" and len(values) != len(set(values)):
            raise ReleaseValidationError(
                "release record installation channels must not contain duplicates"
            )
    return record


def verify_release(
    package_root: Path = PACKAGE_ROOT,
    *,
    tag: str | None = None,
) -> str:
    versions = manifest_versions(package_root)
    if tag is not None:
        versions["release tag"] = tag_version(tag)
    if len(set(versions.values())) != 1:
        raise ReleaseValidationError(f"skills release versions do not match: {versions}")
    validate_release_record(package_root)
    return versions["VERSION"]


def _write_bytes_atomic(path: Path, content: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _write_files_atomically(contents: dict[Path, bytes]) -> None:
    originals = {path: path.read_bytes() for path in contents}
    temporary_paths: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for path, content in contents.items():
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{path.name}.",
                dir=path.parent,
            )
            temporary = Path(temporary_name)
            temporary_paths[path] = temporary
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(content)
        for path, temporary in temporary_paths.items():
            os.replace(temporary, path)
            replaced.append(path)
    except BaseException:
        for path in reversed(replaced):
            _write_bytes_atomic(path, originals[path])
        raise
    finally:
        for temporary in temporary_paths.values():
            temporary.unlink(missing_ok=True)


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def set_version(value: str, package_root: Path = PACKAGE_ROOT) -> None:
    parse_version(value)
    plugin_root = package_root / "plugins" / "polygres"
    manifest_paths = (
        plugin_root / ".codex-plugin" / "plugin.json",
        plugin_root / ".claude-plugin" / "plugin.json",
    )
    contents: dict[Path, bytes] = {}
    for path in manifest_paths:
        manifest = _read_json(path)
        manifest["version"] = value
        contents[path] = _json_bytes(manifest)

    marketplace_path = package_root / ".claude-plugin" / "marketplace.json"
    marketplace = _read_json(marketplace_path)
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
        raise ReleaseValidationError("Claude marketplace must contain exactly one plugin entry")
    entries[0]["version"] = value
    contents[marketplace_path] = _json_bytes(marketplace)
    contents[package_root / "VERSION"] = f"{value}\n".encode()
    _write_files_atomically(contents)


def verify_version_change(base_ref: str, package_root: Path = PACKAGE_ROOT) -> None:
    repository = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=package_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    relative_root = package_root.resolve().relative_to(repository.resolve())
    version_path = (relative_root / "VERSION").as_posix()
    try:
        base_version = subprocess.run(
            ["git", "show", f"{base_ref}:{version_path}"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        manifest_path = (
            relative_root / "plugins" / "polygres" / ".codex-plugin" / "plugin.json"
        ).as_posix()
        try:
            base_manifest = subprocess.run(
                ["git", "show", f"{base_ref}:{manifest_path}"],
                cwd=repository,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        except subprocess.CalledProcessError:
            return
        parsed_manifest = json.loads(base_manifest)
        if not isinstance(parsed_manifest, dict) or not isinstance(
            parsed_manifest.get("version"), str
        ):
            raise ReleaseValidationError("base Codex manifest does not contain a version") from None
        base_version = parsed_manifest["version"]
    parse_version(base_version)
    current_version = canonical_version(package_root)
    changed = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD", "--", relative_root.as_posix()],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    prefix = "" if relative_root == Path(".") else f"{relative_root.as_posix()}/"
    payload_changed = any(
        path.removeprefix(prefix) in {"README.md", "LICENSE"}
        or path.removeprefix(prefix).startswith("plugins/polygres/")
        or path.removeprefix(prefix) == ".agents/plugins/marketplace.json"
        or path.removeprefix(prefix) == ".claude-plugin/marketplace.json"
        for path in changed
    )
    if payload_changed and parse_version(current_version) <= parse_version(base_version):
        raise ReleaseValidationError(
            "installable skills content changed without increasing VERSION"
        )
    if not payload_changed and current_version != base_version:
        raise ReleaseValidationError("VERSION changed without an installable payload change")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="verify release metadata and payload identity")
    check.add_argument("--tag", help=f"optional {TAG_PREFIX}X.Y.Z release tag")
    check.add_argument(
        "--base-ref",
        help="optional Git base used to require a payload version bump",
    )
    subparsers.add_parser("digest", help="print the deterministic release payload digest")
    update = subparsers.add_parser("set", help="update canonical and manifest versions")
    update.add_argument("version")
    args = parser.parse_args(argv)
    try:
        if args.command == "set":
            set_version(args.version)
            print(f"Updated skills release version to {args.version}.")
        elif args.command == "digest":
            print(content_digest())
        else:
            version = verify_release(tag=args.tag)
            if args.base_ref:
                verify_version_change(args.base_ref)
            print(f"Skills release version is consistent: {version}")
    except (OSError, ReleaseValidationError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
