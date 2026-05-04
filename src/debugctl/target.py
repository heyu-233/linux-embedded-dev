from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from debugctl.models import TargetConfig


class TargetConfigError(ValueError):
    """Raised when a target config is missing required structure."""


def load_target_config(path: str | Path) -> TargetConfig:
    target_path = Path(path).expanduser().resolve()
    if not target_path.is_file():
        raise TargetConfigError(f"Target file does not exist: {target_path}")

    with target_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    if not isinstance(raw, dict):
        raise TargetConfigError("Target file must contain a top-level mapping.")

    return parse_target_config(raw, source_path=target_path)


def parse_target_config(raw: dict[str, Any], source_path: Path | None = None) -> TargetConfig:
    name = _require_string(raw, "name")
    target_type = _require_string(raw, "type")
    connect = _require_mapping(raw, "connect")
    runtime = _require_mapping(raw, "runtime")
    evidence = _require_string_list(raw, "evidence")
    build = _optional_mapping(raw, "build")
    deploy = _optional_mapping(raw, "deploy")
    flash = _optional_mapping(raw, "flash")

    config = TargetConfig(
        name=name,
        type=target_type,
        connect=connect,
        runtime=runtime,
        evidence=evidence,
        build=build,
        deploy=deploy,
        flash=flash,
        source_path=source_path,
    )
    _validate_target_type(config)
    return config


def _validate_target_type(config: TargetConfig) -> None:
    if config.type == "linux-board":
        _require_nested_string(config.connect, "connect", "ssh")
        if "workdir" not in config.runtime:
            raise TargetConfigError("linux-board target requires runtime.workdir")
    elif config.type == "mcu":
        _require_nested_string(config.connect, "connect", "serial")
        _require_nested_string(config.flash, "flash", "method")
    else:
        raise TargetConfigError(
            f"Unsupported target type '{config.type}'. Expected 'linux-board' or 'mcu'."
        )


def _require_string(raw: dict[str, Any], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise TargetConfigError(f"Target field '{key}' must be a non-empty string.")
    return value


def _require_mapping(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key)
    if not isinstance(value, dict):
        raise TargetConfigError(f"Target field '{key}' must be a mapping.")
    return value


def _optional_mapping(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise TargetConfigError(f"Target field '{key}' must be a mapping when provided.")
    return value


def _require_string_list(raw: dict[str, Any], key: str) -> list[str]:
    value = raw.get(key)
    if not isinstance(value, list) or not value:
        raise TargetConfigError(f"Target field '{key}' must be a non-empty list.")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise TargetConfigError(f"Every item in '{key}' must be a non-empty string.")
        normalized.append(item)
    return normalized


def _require_nested_string(raw: dict[str, Any], group: str, key: str) -> None:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise TargetConfigError(f"{group}.{key} must be a non-empty string.")
