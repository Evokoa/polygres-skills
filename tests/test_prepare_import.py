from __future__ import annotations

import importlib.util
import json
import sys
from argparse import Namespace
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).parents[1]
    / "plugins"
    / "polygres"
    / "skills"
    / "polygres-cli"
    / "scripts"
    / "prepare_import.py"
)
SPEC = importlib.util.spec_from_file_location("prepare_import", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
prepare_import = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = prepare_import
SPEC.loader.exec_module(prepare_import)


def args(source: Path, output: Path, **overrides: object) -> Namespace:
    values: dict[str, object] = {
        "input_file": source,
        "format": "auto",
        "output": output,
        "nested": "reject",
        "key_style": "preserve",
        "allow_single_object": False,
        "no_header": False,
        "overwrite": False,
        "json_output": True,
        "max_output_bytes": prepare_import.MAX_OUTPUT_BYTES,
    }
    values.update(overrides)
    return Namespace(**values)


def read_csv(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def test_json_array_prepares_deterministic_csv(tmp_path: Path) -> None:
    source = tmp_path / "rows.json"
    output = tmp_path / "rows.csv"
    source.write_text(
        json.dumps([{"id": 1, "active": True}, {"active": False, "name": "Ada"}]),
        encoding="utf-8",
    )

    manifest = prepare_import.run(args(source, output))

    assert manifest["source_format"] == "json"
    assert manifest["row_count"] == 2
    assert manifest["columns"] == ["id", "active", "name"]
    assert read_csv(output) == ["id,active,name", "1,true,", ",false,Ada"]
    assert len(manifest["source_sha256"]) == 64
    assert len(manifest["output_sha256"]) == 64


def test_json_array_is_incremental_across_small_buffers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "rows.json"
    output = tmp_path / "rows.csv"
    source.write_text('[{"identifier":1},{"identifier":2}]', encoding="utf-8")
    monkeypatch.setattr(prepare_import, "READ_CHUNK_SIZE", 4)

    manifest = prepare_import.run(args(source, output))

    assert manifest["row_count"] == 2
    assert read_csv(output) == ["identifier", "1", "2"]


def test_nested_json_rejects_without_output(tmp_path: Path) -> None:
    source = tmp_path / "rows.json"
    output = tmp_path / "rows.csv"
    source.write_text('[{"id":1,"metadata":{"source":"web"}}]', encoding="utf-8")

    with pytest.raises(prepare_import.PreparationError, match="Nested JSON fields"):
        prepare_import.run(args(source, output))

    assert not output.exists()


def test_nested_json_stringifies_compact_json(tmp_path: Path) -> None:
    source = tmp_path / "rows.json"
    output = tmp_path / "rows.csv"
    source.write_text('[{"id":1,"metadata":{"b":2,"a":1}}]', encoding="utf-8")

    manifest = prepare_import.run(args(source, output, nested="stringify"))

    assert manifest["nested_fields"] == ["metadata"]
    assert "compact JSON text" in manifest["warnings"][-1]
    assert read_csv(output)[1] == '1,"{""a"":1,""b"":2}"'


def test_nested_json_flattens_objects_and_rejects_arrays(tmp_path: Path) -> None:
    source = tmp_path / "rows.json"
    output = tmp_path / "rows.csv"
    source.write_text('[{"profile":{"name":"Ada"}}]', encoding="utf-8")

    manifest = prepare_import.run(args(source, output, nested="flatten"))

    assert manifest["columns"] == ["profile_name"]
    assert manifest["nested_fields"] == ["profile"]
    assert read_csv(output) == ["profile_name", "Ada"]

    array_source = tmp_path / "array.json"
    array_output = tmp_path / "array.csv"
    array_source.write_text('[{"tags":["a","b"]}]', encoding="utf-8")
    with pytest.raises(prepare_import.PreparationError, match="Cannot flatten JSON array"):
        prepare_import.run(args(array_source, array_output, nested="flatten"))
    assert not array_output.exists()


def test_sql_safe_key_mapping_and_collision(tmp_path: Path) -> None:
    source = tmp_path / "rows.json"
    output = tmp_path / "rows.csv"
    source.write_text('[{"full name":"Ada","2026 total":4}]', encoding="utf-8")

    manifest = prepare_import.run(args(source, output, key_style="sql-safe"))

    assert manifest["key_mapping"] == {
        "full name": "full_name",
        "2026 total": "c_2026_total",
    }
    assert manifest["columns"] == ["full_name", "c_2026_total"]

    collision = tmp_path / "collision.json"
    collision.write_text('[{"a-b":1,"a b":2}]', encoding="utf-8")
    with pytest.raises(prepare_import.PreparationError, match="collisions"):
        prepare_import.run(
            args(collision, tmp_path / "collision.csv", key_style="sql-safe")
        )


def test_preserve_rejects_invalid_sql_identifier(tmp_path: Path) -> None:
    source = tmp_path / "rows.json"
    source.write_text('[{"full name":"Ada"}]', encoding="utf-8")

    with pytest.raises(prepare_import.PreparationError, match="not valid SQL identifiers"):
        prepare_import.run(args(source, tmp_path / "rows.csv"))


def test_null_empty_string_conflict_is_reported(tmp_path: Path) -> None:
    source = tmp_path / "rows.json"
    output = tmp_path / "rows.csv"
    source.write_text('[{"value":null},{"value":""},{}]', encoding="utf-8")

    manifest = prepare_import.run(args(source, output))

    assert manifest["null_empty_string_conflicts"] == ["value"]
    assert "cannot remain distinct" in manifest["warnings"][0]


def test_jsonl_ignores_blank_lines_and_requires_objects(tmp_path: Path) -> None:
    source = tmp_path / "rows.jsonl"
    output = tmp_path / "rows.csv"
    source.write_text('{"id":1}\n\n{"id":2}\n', encoding="utf-8")

    manifest = prepare_import.run(args(source, output))

    assert manifest["source_format"] == "jsonl"
    assert manifest["row_count"] == 2

    invalid = tmp_path / "invalid.jsonl"
    invalid.write_text('{"id":1}\n[2]\n', encoding="utf-8")
    with pytest.raises(prepare_import.PreparationError, match="line 2 must contain an object"):
        prepare_import.run(args(invalid, tmp_path / "invalid.csv"))


def test_malformed_jsonl_reports_location_without_row_value(tmp_path: Path) -> None:
    source = tmp_path / "rows.jsonl"
    source.write_text('{"id":1}\n{"id":}\n', encoding="utf-8")

    with pytest.raises(prepare_import.PreparationError, match="Malformed JSONL on line 2"):
        prepare_import.run(args(source, tmp_path / "rows.csv"))


def test_single_json_object_requires_explicit_flag(tmp_path: Path) -> None:
    source = tmp_path / "row.json"
    output = tmp_path / "row.csv"
    source.write_text('{"id":1}', encoding="utf-8")

    with pytest.raises(prepare_import.PreparationError, match="allow-single-object"):
        prepare_import.run(args(source, output))

    manifest = prepare_import.run(args(source, output, allow_single_object=True))
    assert manifest["row_count"] == 1
    assert read_csv(output) == ["id", "1"]


def test_tsv_and_utf8_bom_are_normalized(tmp_path: Path) -> None:
    source = tmp_path / "rows.tsv"
    output = tmp_path / "rows.csv"
    source.write_text("\ufeffid\tname\n1\tZoë\n", encoding="utf-8")

    manifest = prepare_import.run(args(source, output))

    assert manifest["source_format"] == "tsv"
    assert read_csv(output) == ["id,name", "1,Zoë"]


def test_headerless_csv_generates_columns(tmp_path: Path) -> None:
    source = tmp_path / "rows.csv"
    output = tmp_path / "rows-output.csv"
    source.write_text("1,Ada\n2,Grace\n", encoding="utf-8")

    manifest = prepare_import.run(args(source, output, no_header=True))

    assert manifest["columns"] == ["column_1", "column_2"]
    assert manifest["row_count"] == 2
    assert read_csv(output) == ["column_1,column_2", "1,Ada", "2,Grace"]


def test_inconsistent_delimited_rows_fail(tmp_path: Path) -> None:
    source = tmp_path / "rows.csv"
    source.write_text("id,name\n1,Ada\n2\n", encoding="utf-8")

    with pytest.raises(prepare_import.PreparationError, match="has 1 fields; expected 2"):
        prepare_import.run(args(source, tmp_path / "rows-output.csv"))


def test_format_extension_conflict_fails(tmp_path: Path) -> None:
    source = tmp_path / "rows.csv"
    source.write_text("id\n1\n", encoding="utf-8")

    with pytest.raises(prepare_import.PreparationError, match="conflicts with file extension"):
        prepare_import.run(args(source, tmp_path / "rows-output.csv", format="json"))


def test_output_limit_failure_is_atomic(tmp_path: Path) -> None:
    source = tmp_path / "rows.json"
    output = tmp_path / "rows.csv"
    source.write_text('[{"identifier":"a long value"}]', encoding="utf-8")

    with pytest.raises(prepare_import.PreparationError, match="output-size limit"):
        prepare_import.run(args(source, output, max_output_bytes=5))

    assert not output.exists()
    assert not list(tmp_path.glob(".rows.csv.*.tmp"))


def test_existing_output_and_source_overwrite_are_rejected(tmp_path: Path) -> None:
    source = tmp_path / "rows.csv"
    output = tmp_path / "output.csv"
    source.write_text("id\n1\n", encoding="utf-8")
    output.write_text("existing", encoding="utf-8")

    with pytest.raises(prepare_import.PreparationError, match="already exists"):
        prepare_import.run(args(source, output))
    with pytest.raises(prepare_import.PreparationError, match="must not overwrite"):
        prepare_import.run(args(source, source))


def test_main_json_mode_separates_stdout_and_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "rows.json"
    output = tmp_path / "rows.csv"
    source.write_text('[{"id":1}]', encoding="utf-8")

    result = prepare_import.main(
        [str(source), "--output", str(output), "--format", "json", "--json"]
    )
    captured = capsys.readouterr()

    assert result == 0
    assert json.loads(captured.out)["row_count"] == 1
    assert captured.err == ""


def test_main_error_writes_only_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "rows.json"
    source.write_text("not-json", encoding="utf-8")

    result = prepare_import.main(
        [str(source), "--output", str(tmp_path / "rows.csv"), "--format", "json", "--json"]
    )
    captured = capsys.readouterr()

    assert result == 2
    assert captured.out == ""
    assert captured.err.startswith("prepare_import:")
