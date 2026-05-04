from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from debugctl.models import TargetConfig


def build_target_snapshot(config: TargetConfig) -> dict[str, Any]:
    return {
        "name": config.name,
        "type": config.type,
        "connect": config.connect,
        "build": config.build,
        "deploy": config.deploy,
        "flash": config.flash,
        "runtime": config.runtime,
        "evidence": config.evidence,
        "source_path": str(config.source_path) if config.source_path else None,
    }


def create_bundle_dir(path: str | Path) -> Path:
    bundle_dir = Path(path).expanduser().resolve()
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "commands").mkdir(exist_ok=True)
    (bundle_dir / "artifacts").mkdir(exist_ok=True)
    return bundle_dir


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, body: str) -> None:
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def sha256_file(path: str | Path) -> str:
    file_path = Path(path).expanduser().resolve()
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()
