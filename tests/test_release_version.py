from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

PACKAGE_ROOT = Path(__file__).parents[1]
SCRIPT = PACKAGE_ROOT / "scripts" / "release_version.py"


def _load_release_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("skills_release_version", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RELEASE = _load_release_module()


def _copy_package(tmp_path: Path) -> Path:
    destination = tmp_path / "agent-skills"
    shutil.copytree(
        PACKAGE_ROOT,
        destination,
        ignore=shutil.ignore_patterns(".pytest_cache", ".ruff_cache", "__pycache__", "*.pyc"),
    )
    return destination


def _run(package: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(package / "scripts" / "release_version.py"), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def test_release_contract_matches_version_manifests_record_and_digest() -> None:
    result = _run(PACKAGE_ROOT, "check", "--tag", "polygres-skills-v0.4.0")

    assert result.returncode == 0, result.stderr
    assert result.stdout == "Skills release version is consistent: 0.4.0\n"


def test_release_targets_current_clients_and_skills_050() -> None:
    record = json.loads((PACKAGE_ROOT / "releases" / "0.4.0.json").read_text())
    readme = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")

    assert RELEASE.canonical_version(PACKAGE_ROOT) == "0.4.0"
    assert record["version"] == "0.4.0"
    assert record["release_date"] == "2026-08-14"
    assert record["compatibility"]["polygres_cli"] == {
        "minimum_supported": "0.3.0",
        "maximum_tested": "0.3.0",
    }
    assert record["compatibility"]["polygres_sdk"] == {
        "minimum_supported": "0.3.0",
        "maximum_tested": "0.3.0",
    }
    assert "Package version: [`0.4.0`]" in readme
    assert "polygres-cli 0.3.0" in readme
    assert "polygres-sdk 0.3.0" in readme


@pytest.mark.parametrize(
    "tag",
    (
        "polygres-skills-v0.3",
        "polygres-skills-v0.3.0-rc.1",
        "polygres-skills-v03.0.0",
        "python-skills-v0.3.0",
    ),
)
def test_release_tag_requires_exact_stable_semver(tag: str) -> None:
    with pytest.raises(RELEASE.ReleaseValidationError, match="exact"):
        RELEASE.tag_version(tag)


def test_manifest_mismatch_is_rejected(tmp_path: Path) -> None:
    package = _copy_package(tmp_path)
    manifest_path = package / "plugins" / "polygres" / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["version"] = "0.4.1"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    result = _run(package, "check")

    assert result.returncode == 2
    assert "skills release versions do not match" in result.stderr


def test_payload_digest_is_deterministic_and_scoped(tmp_path: Path) -> None:
    package = _copy_package(tmp_path)
    initial = RELEASE.content_digest(package)

    (package / "tests" / "internal-only.txt").write_text("does not ship\n")
    assert RELEASE.content_digest(package) == initial

    skill = package / "plugins" / "polygres" / "skills" / "polygres-sdk" / "SKILL.md"
    skill.write_text(skill.read_text() + "\nBehavioral release change.\n")
    assert RELEASE.content_digest(package) != initial


def test_release_record_rejects_payload_drift(tmp_path: Path) -> None:
    package = _copy_package(tmp_path)
    skill = package / "plugins" / "polygres" / "skills" / "polygres-sdk" / "SKILL.md"
    skill.write_text(skill.read_text().replace("Build Python", "Develop Python", 1))

    with pytest.raises(RELEASE.ReleaseValidationError, match="digest does not match"):
        RELEASE.validate_release_record(package)


def test_set_updates_all_machine_readable_version_copies(tmp_path: Path) -> None:
    package = _copy_package(tmp_path)

    RELEASE.set_version("0.5.1", package)
    versions = RELEASE.manifest_versions(package)

    assert set(versions.values()) == {"0.5.1"}
    assert (package / "VERSION").read_text() == "0.5.1\n"


def test_set_rolls_back_every_version_copy_after_a_write_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = _copy_package(tmp_path)
    paths = (
        package / "VERSION",
        package / "plugins" / "polygres" / ".codex-plugin" / "plugin.json",
        package / "plugins" / "polygres" / ".claude-plugin" / "plugin.json",
        package / ".claude-plugin" / "marketplace.json",
    )
    originals = {path: path.read_bytes() for path in paths}
    real_replace = RELEASE.os.replace
    calls = 0

    def fail_second_replace(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated interrupted release update")
        real_replace(source, destination)

    monkeypatch.setattr(RELEASE.os, "replace", fail_second_replace)

    with pytest.raises(OSError, match="simulated interrupted"):
        RELEASE.set_version("0.4.1", package)

    assert {path: path.read_bytes() for path in paths} == originals


def test_payload_change_requires_a_version_increase(tmp_path: Path) -> None:
    package = _copy_package(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=package, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=package, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=package, check=True)
    subprocess.run(["git", "add", "."], cwd=package, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=package, check=True)
    skill = package / "plugins" / "polygres" / "skills" / "polygres-sdk" / "SKILL.md"
    skill.write_text(skill.read_text() + "\nVersioned behavior.\n")
    subprocess.run(["git", "add", "."], cwd=package, check=True)
    subprocess.run(["git", "commit", "-qm", "change payload"], cwd=package, check=True)

    with pytest.raises(RELEASE.ReleaseValidationError, match="without increasing VERSION"):
        RELEASE.verify_version_change("HEAD~1", package)

    RELEASE.set_version("0.5.1", package)
    RELEASE.verify_version_change("HEAD~1", package)


def test_readme_change_does_not_require_a_version_increase(tmp_path: Path) -> None:
    package = _copy_package(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=package, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=package, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=package, check=True)
    subprocess.run(["git", "add", "."], cwd=package, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=package, check=True)
    readme = package / "README.md"
    readme.write_text(readme.read_text() + "\nDocumentation correction.\n")
    subprocess.run(["git", "add", "README.md"], cwd=package, check=True)
    subprocess.run(["git", "commit", "-qm", "correct readme"], cwd=package, check=True)

    RELEASE.verify_version_change("HEAD~1", package)


def test_version_change_check_bootstraps_from_existing_manifest(tmp_path: Path) -> None:
    package = _copy_package(tmp_path)
    version_contents = (package / "VERSION").read_text()
    (package / "VERSION").unlink()
    subprocess.run(["git", "init", "-q"], cwd=package, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=package, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=package, check=True)
    subprocess.run(["git", "add", "."], cwd=package, check=True)
    subprocess.run(
        ["git", "commit", "-qm", "baseline without canonical version"],
        cwd=package,
        check=True,
    )
    (package / "VERSION").write_text(version_contents)
    subprocess.run(["git", "add", "VERSION"], cwd=package, check=True)
    subprocess.run(["git", "commit", "-qm", "add canonical version"], cwd=package, check=True)

    RELEASE.verify_version_change("HEAD~1", package)
