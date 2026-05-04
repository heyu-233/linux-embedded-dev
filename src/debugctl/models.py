from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class TargetConfig:
    name: str
    type: str
    connect: dict[str, Any]
    runtime: dict[str, Any]
    evidence: list[str]
    build: dict[str, Any] = field(default_factory=dict)
    deploy: dict[str, Any] = field(default_factory=dict)
    flash: dict[str, Any] = field(default_factory=dict)
    source_path: Path | None = None


@dataclass(slots=True)
class CommandResult:
    command: str
    ok: bool
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
    bundle_path: Path | None = None


@dataclass(slots=True)
class ToolStatus:
    name: str
    available: bool
    path: str | None = None
    version: str | None = None
    note: str | None = None
