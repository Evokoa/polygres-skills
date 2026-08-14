#!/usr/bin/env python3
"""Rank compatible local and hosted embedding choices without prompting or networking."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

SCRIPT_ROOT = Path(__file__).resolve().parent
SOURCE_CATALOG = SCRIPT_ROOT.parent / "assets" / "embedding-models.json"
SCAFFOLDED_CATALOG = SCRIPT_ROOT.parent / "embedding-models.json"
DEFAULT_CATALOG = SCAFFOLDED_CATALOG if SCAFFOLDED_CATALOG.is_file() else SOURCE_CATALOG
VALID_PREFERENCES = {"unknown", "local", "hosted", "existing"}


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read {label}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _requirements(value: dict[str, Any]) -> dict[str, Any]:
    preference = str(value.get("deployment_preference", "unknown")).casefold()
    if preference not in VALID_PREFERENCES:
        raise ValueError("deployment_preference must be unknown, local, hosted, or existing")
    languages = value.get("languages", ["en"])
    if not isinstance(languages, list) or not languages:
        raise ValueError("languages must be a non-empty list")
    max_chunk_tokens = value.get("max_chunk_tokens", 512)
    if not isinstance(max_chunk_tokens, int) or max_chunk_tokens < 1:
        raise ValueError("max_chunk_tokens must be a positive integer")
    dimensions = value.get("existing_dimensions")
    if dimensions is not None and (not isinstance(dimensions, int) or dimensions < 1):
        raise ValueError("existing_dimensions must be a positive integer or null")
    return {
        "deployment_preference": preference,
        "languages": [str(item).casefold() for item in languages],
        "max_chunk_tokens": max_chunk_tokens,
        "contains_code": bool(value.get("contains_code", False)),
        "commercial_use": bool(value.get("commercial_use", True)),
        "external_processing_allowed": bool(value.get("external_processing_allowed", True)),
        "existing_dimensions": dimensions,
        "preferred_runtime": value.get("preferred_runtime"),
        "preferred_provider": value.get("preferred_provider"),
    }


def _language_compatible(model: dict[str, Any], required: list[str]) -> bool:
    supported = {str(item).casefold() for item in model.get("languages", [])}
    if "multilingual" in supported:
        return True
    return set(required) <= supported


def _dimension_compatible(model: dict[str, Any], required: int | None) -> bool:
    if required is None:
        return True
    return required in model.get("dimensions", {}).get("allowed", [])


def _installed_names(device: dict[str, Any]) -> set[str]:
    values = device.get("ollama_models", [])
    return {str(item).casefold() for item in values} if isinstance(values, list) else set()


def _available_memory(device: dict[str, Any]) -> float | None:
    value = device.get("memory_available_gib", device.get("memory_gib"))
    return float(value) if isinstance(value, (int, float)) and math.isfinite(value) else None


def _local_candidates(
    catalog: dict[str, Any], requirements: dict[str, Any], device: dict[str, Any]
) -> list[dict[str, Any]]:
    memory = _available_memory(device)
    disk = device.get("disk_free_gib")
    installed = _installed_names(device)
    commands = device.get("commands") if isinstance(device.get("commands"), dict) else {}
    modules = device.get("python_modules") if isinstance(device.get("python_modules"), dict) else {}
    runtime_ready = {
        "ollama": bool(commands.get("ollama")),
        "sentence-transformers": bool(modules.get("sentence_transformers")),
        "onnx": bool(modules.get("onnxruntime")),
    }
    candidates: list[dict[str, Any]] = []
    for raw in catalog.get("local", []):
        model = dict(raw)
        if requirements["commercial_use"] and not model.get("commercial_use", False):
            continue
        if not _language_compatible(model, requirements["languages"]):
            continue
        if requirements["contains_code"] and "code" not in model.get("languages", []):
            continue
        if model.get("context_tokens", 0) < requirements["max_chunk_tokens"]:
            continue
        if not _dimension_compatible(model, requirements["existing_dimensions"]):
            continue
        if memory is not None and memory < float(model.get("minimum_memory_gib", 0)):
            continue
        download_gib = float(model.get("download_bytes", 0)) / (1024**3)
        if isinstance(disk, (int, float)) and disk < max(1.0, download_gib * 1.5):
            continue
        runtimes = model.get("runtimes", [])
        preferred_runtime = requirements["preferred_runtime"]
        if preferred_runtime and preferred_runtime not in runtimes:
            continue
        aliases = {str(item).casefold() for item in model.get("runtime_aliases", [])}
        is_installed = bool(installed & aliases)
        ready_runtimes = [runtime for runtime in runtimes if runtime_ready.get(runtime)]
        score = float(model.get("popularity_weight", 0))
        score += 100 if is_installed else 0
        score += 20 if ready_runtimes else 0
        score += 12 if requirements["contains_code"] and "code" in model["languages"] else 0
        score += 6 if len(requirements["languages"]) > 1 else 0
        score -= download_gib
        model["category"] = "local"
        model["installed"] = is_installed
        model["ready_runtimes"] = ready_runtimes
        if is_installed:
            reason = "already installed and compatible with the inspected data"
            setup = "reuse the installed model; do not download another model"
        elif ready_runtimes:
            reason = f"compatible with the data and the ready {ready_runtimes[0]} runtime"
            setup = f"download the pinned {model['model']} model"
        else:
            reason = "compatible with the inspected data and device resources"
            setup = f"install a supported runtime and download the pinned {model['model']} model"
        model["reason"] = reason
        model["setup_action"] = setup
        model["_score"] = score
        candidates.append(model)
    return sorted(candidates, key=lambda item: (-item["_score"], item["id"]))


def _hosted_candidates(
    catalog: dict[str, Any], requirements: dict[str, Any]
) -> list[dict[str, Any]]:
    if not requirements["external_processing_allowed"]:
        return []
    candidates: list[dict[str, Any]] = []
    for raw in catalog.get("hosted", []):
        model = dict(raw)
        if not _language_compatible(model, requirements["languages"]):
            continue
        if requirements["contains_code"] and "code" not in model.get("languages", []):
            continue
        if model.get("context_tokens", 0) < requirements["max_chunk_tokens"]:
            continue
        if not _dimension_compatible(model, requirements["existing_dimensions"]):
            continue
        preferred_provider = requirements["preferred_provider"]
        score = float(model.get("popularity_weight", 0))
        score += 40 if preferred_provider and model.get("provider") == preferred_provider else 0
        score += 30 if requirements["contains_code"] and model.get("id") == "voyage-code-3" else 0
        score -= float(model.get("price_usd_per_million_tokens", 0)) * 10
        model["category"] = "hosted"
        model["reason"] = (
            "optimized for code retrieval with a long hosted context window"
            if requirements["contains_code"] and model.get("id") == "voyage-code-3"
            else "compatible hosted default with no local model download"
        )
        model["setup_action"] = (
            f"set {model['credential_name']} locally and send filtered embedding inputs "
            f"to {model['provider']}"
        )
        model["data_egress"] = f"filtered embedding inputs are sent to {model['provider']}"
        model["paid_processing"] = True
        model["_score"] = score
        candidates.append(model)
    return sorted(candidates, key=lambda item: (-item["_score"], item["id"]))


def _public(model: dict[str, Any] | None) -> dict[str, Any] | None:
    if model is None:
        return None
    return {key: value for key, value in model.items() if not key.startswith("_")}


def recommend(
    catalog: dict[str, Any], requirements_value: dict[str, Any], device: dict[str, Any]
) -> dict[str, Any]:
    requirements = _requirements(requirements_value)
    preference = requirements["deployment_preference"]
    if preference == "existing":
        return {
            "status": "reuse-existing",
            "preference_resolved": True,
            "catalog_version": catalog.get("version"),
            "catalog_verified_at": catalog.get("verified_at"),
            "recommended": {
                "category": "existing",
                "reason": "reuse compatible source vectors and preserve their exact model contract",
            },
            "alternative": None,
            "blockers": [],
            "warnings": [],
        }
    local = _local_candidates(catalog, requirements, device)
    hosted = _hosted_candidates(catalog, requirements)
    recommended: dict[str, Any] | None
    alternative: dict[str, Any] | None
    if preference == "local":
        recommended = local[0] if local else None
        alternative = None
    elif preference == "hosted":
        recommended = hosted[0] if hosted else None
        alternative = None
    else:
        recommended = local[0] if local else (hosted[0] if hosted else None)
        alternative = hosted[0] if local and hosted else None
    blockers = []
    if recommended is None:
        blockers.append(
            {
                "code": "no-compatible-embedding-model",
                "message": (
                    "No catalog model fits the inspected requirements and allowed "
                    "processing boundary."
                ),
            }
        )
    return {
        "status": "ready" if recommended else "blocked",
        "preference_resolved": preference != "unknown" or not (local and hosted),
        "catalog_version": catalog.get("version"),
        "catalog_verified_at": catalog.get("verified_at"),
        "recommended": _public(recommended),
        "alternative": _public(alternative),
        "blockers": blockers,
        "warnings": [],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requirements", required=True, type=Path)
    parser.add_argument("--device", required=True, type=Path)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args(argv)
    try:
        report = recommend(
            _load_object(args.catalog, "catalog"),
            _load_object(args.requirements, "requirements"),
            _load_object(args.device, "device report"),
        )
    except ValueError as error:
        print(f"recommendation failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
