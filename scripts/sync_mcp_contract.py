#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = PACKAGE_ROOT / "plugins" / "polygres"
SOURCE = PLUGIN_ROOT / "references" / "mcp-tool-contract.md"
SKILLS = (
    "polygres-cli",
    "polygres-data-pipeline",
    "polygres-retrieval-design",
    "polygres-sdk",
    "polygres-troubleshooting",
)


def rendered_contract(source: bytes) -> bytes:
    digest = hashlib.sha256(source).hexdigest()
    header = (
        "<!-- Generated from ../../../references/mcp-tool-contract.md; "
        f"source-sha256: {digest} -->\n\n"
    ).encode()
    return header + source


def sync() -> None:
    source = SOURCE.read_bytes()
    rendered = rendered_contract(source)
    for skill in SKILLS:
        target = PLUGIN_ROOT / "skills" / skill / "references" / "mcp-tool-contract.md"
        target.write_bytes(rendered)


if __name__ == "__main__":
    sync()
