from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).parents[1]
MONOREPO_ROOT = PACKAGE_ROOT.parents[1]
REFERENCE = (
    PACKAGE_ROOT
    / "plugins"
    / "polygres"
    / "skills"
    / "polygres-troubleshooting"
    / "references"
    / "embeddings.md"
)
CATALOG = MONOREPO_ROOT / "packages" / "polygres-lib" / "contracts" / "errors" / "catalog.json"


@pytest.mark.skipif(not CATALOG.is_file(), reason="Public error catalog is not in this checkout")
def test_embedding_recovery_table_matches_public_error_contract() -> None:
    errors = {record["code"]: record for record in json.loads(CATALOG.read_text())["errors"]}
    rows = re.findall(
        r"^\| `(\w+)` \| (\d+) \| `(\w+)` \|",
        REFERENCE.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    assert rows
    assert len({code for code, _, _ in rows}) == len(rows)
    for code, status, retry_class in rows:
        record = errors[code]
        assert record["visibility"] == "public", code
        assert int(status) == record["http_status"], code
        assert retry_class == record["retry_class"], code

    documented = {code: (status, retry_class) for code, status, retry_class in rows}
    assert documented["EMBEDDING_QUOTA_EXHAUSTED"] == ("429", "after_user_action")
    assert documented["EMBEDDING_PROVIDER_RATE_LIMITED"] == ("429", "after_delay")
    assert documented["EMBEDDING_PROVIDER_OUTCOME_UNKNOWN"] == ("409", "after_user_action")
