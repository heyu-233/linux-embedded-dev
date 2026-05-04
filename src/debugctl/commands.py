from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from debugctl.models import CommandResult, TargetConfig
from debugctl.mcu import McuBackend
from debugctl.runtime import (
    build_target_snapshot,
    create_bundle_dir,
    now_iso,
    sha256_file,
    write_json,
    write_text,
)
from debugctl.transport import LinuxBoardAdapter, RemoteProcessResult

EVIDENCE_COMMANDS = {
    "uname": "uname -a",
    "dmesg_tail": "dmesg | tail -n 200",
    "dev_nodes": "find /dev -maxdepth 2 -type c -o -type b",
    "modules": "lsmod",
    "disk": "df -h",
    "serial_log": "<serial capture>",
    "flash_log": "<flash tool log>",
    "reset_result": "<reset status>",
}


def status_command(config: TargetConfig) -> CommandResult:
    if config.type == "mcu":
        return McuBackend(config).status()
    if config.type != "linux-board":
        return CommandResult(
            command="status",
            ok=True,
            summary=f"Loaded target '{config.name}' ({config.type}); transport probing is not implemented for this target type.",
            details={
                "target_name": config.name,
                "target_type": config.type,
                "source_path": str(config.source_path) if config.source_path else None,
                "connect": config.connect,
                "runtime": config.runtime,
                "evidence_count": len(config.evidence),
                "supported_commands": ["status", "collect", "deploy", "run", "diagnose"],
                "prototype_mode": True,
            },
        )

    adapter = LinuxBoardAdapter(config)
    probe = adapter.probe()
    workdir = adapter.ensure_workdir() if probe.ok else None
    ok = probe.ok and workdir is not None and workdir.ok
    summary = (
        f"Connected to target '{config.name}' and verified runtime workdir."
        if ok
        else f"Could not verify target '{config.name}' connectivity or workdir."
    )
    details = {
        "target_name": config.name,
        "target_type": config.type,
        "source_path": str(config.source_path) if config.source_path else None,
        "connect": config.connect,
        "runtime": config.runtime,
        "evidence_count": len(config.evidence),
        "supported_commands": ["status", "collect", "deploy", "run", "diagnose"],
        "probe": _result_dict(probe),
        "workdir_check": _result_dict(workdir) if workdir is not None else None,
        "prototype_mode": False,
    }
    return CommandResult(command="status", ok=ok, summary=summary, details=details)


def collect_command(config: TargetConfig, out_dir: str | Path) -> CommandResult:
    bundle_dir = create_bundle_dir(out_dir)
    target_snapshot = build_target_snapshot(config)
    if config.type == "mcu":
        return _collect_mcu(config, bundle_dir, target_snapshot)
    if config.type != "linux-board":
        return _collect_planned_only(config, bundle_dir, target_snapshot)

    adapter = LinuxBoardAdapter(config)
    workdir = adapter.ensure_workdir()
    evidence_plan: list[dict[str, str]] = []
    command_results: list[dict[str, object]] = []
    all_ok = workdir.ok

    write_json(bundle_dir / "target.json", target_snapshot)

    for index, item in enumerate(config.evidence, start=1):
        command_name = f"{index:02d}-{item}"
        shell_command = EVIDENCE_COMMANDS.get(item)
        evidence_plan.append({"name": item, "command": shell_command or "<unsupported evidence>"})
        if shell_command is None:
            stdout = ""
            stderr = f"Unsupported evidence item: {item}"
            returncode = 2
        else:
            remote = adapter.run(shell_command)
            stdout = remote.stdout
            stderr = remote.stderr
            returncode = remote.returncode

        write_text(bundle_dir / "commands" / f"{command_name}.stdout.txt", stdout)
        write_text(bundle_dir / "commands" / f"{command_name}.stderr.txt", stderr)
        command_results.append(
            {
                "name": item,
                "command": shell_command or "<unsupported evidence>",
                "returncode": returncode,
            }
        )
        all_ok = all_ok and returncode == 0

    execution_state = "completed" if all_ok else "partial-failure"
    manifest = {
        "created_at": now_iso(),
        "bundle_kind": "debugctl-evidence",
        "prototype_mode": False,
        "target_name": config.name,
        "target_type": config.type,
        "evidence_plan": evidence_plan,
        "execution_state": execution_state,
        "workdir_check": _result_dict(workdir),
        "command_results": command_results,
    }

    write_json(bundle_dir / "manifest.json", manifest)
    write_text(
        bundle_dir / "diagnosis.md",
        _diagnosis_markdown(manifest),
    )
    write_text(
        bundle_dir / "run-summary.md",
        "\n".join(
            [
                "# Run Summary",
                "",
                f"- Target: `{config.name}`",
                f"- Type: `{config.type}`",
                f"- Evidence items: `{len(config.evidence)}`",
                f"- Status: `{execution_state}`",
            ]
        ),
    )

    summary = f"Collected evidence bundle at {bundle_dir}" if all_ok else f"Collected partial evidence bundle at {bundle_dir}"
    details = {
        "bundle_path": str(bundle_dir),
        "evidence_items": config.evidence,
        "execution_state": execution_state,
        "workdir_check": _result_dict(workdir),
    }
    return CommandResult(
        command="collect",
        ok=all_ok,
        summary=summary,
        details=details,
        bundle_path=bundle_dir,
    )


def deploy_command(config: TargetConfig, artifact: str | Path) -> CommandResult:
    artifact_path = Path(artifact).expanduser().resolve()
    if not artifact_path.is_file():
        return CommandResult(
            command="deploy",
            ok=False,
            summary=f"Artifact does not exist: {artifact_path}",
        )

    if config.type == "mcu":
        return McuBackend(config).flash(artifact_path)
    digest = sha256_file(artifact_path)
    if config.type != "linux-board":
        return CommandResult(
            command="deploy",
            ok=True,
            summary="Validated local artifact; remote deploy is not implemented for this target type.",
            details={
                "artifact_path": str(artifact_path),
                "artifact_sha256": digest,
                "target_name": config.name,
                "deploy_method": config.deploy.get("method"),
                "prototype_mode": True,
            },
        )

    adapter = LinuxBoardAdapter(config)
    workdir = config.runtime.get("workdir")
    remote_path = f"{workdir.rstrip('/')}/{artifact_path.name}"
    prep = adapter.ensure_workdir()
    if not prep.ok:
        return CommandResult(
            command="deploy",
            ok=False,
            summary="Failed to prepare remote workdir before deploy.",
            details={
                "target_name": config.name,
                "workdir_prepare": _result_dict(prep),
            },
        )

    upload = adapter.copy_to(artifact_path, remote_path)
    if not upload.ok:
        return CommandResult(
            command="deploy",
            ok=False,
            summary="Artifact upload failed.",
            details={
                "target_name": config.name,
                "artifact_path": str(artifact_path),
                "remote_path": remote_path,
                "artifact_sha256": digest,
                "upload": _result_dict(upload),
            },
        )

    remote_sha = adapter.read_remote_sha256(remote_path)
    remote_digest = remote_sha.stdout.strip()
    ok = remote_sha.ok and remote_digest == digest
    summary = "Uploaded artifact and verified remote SHA-256." if ok else "Uploaded artifact but remote SHA-256 verification failed."
    details = {
        "artifact_path": str(artifact_path),
        "artifact_sha256": digest,
        "remote_artifact_path": remote_path,
        "remote_artifact_sha256": remote_digest,
        "target_name": config.name,
        "deploy_method": config.deploy.get("method"),
        "workdir_prepare": _result_dict(prep),
        "upload": _result_dict(upload),
        "remote_sha256": _result_dict(remote_sha),
        "prototype_mode": False,
    }
    return CommandResult(command="deploy", ok=ok, summary=summary, details=details)


def flash_command(config: TargetConfig, artifact: str | Path) -> CommandResult:
    return McuBackend(config).flash(artifact)


def reset_command(config: TargetConfig) -> CommandResult:
    return McuBackend(config).reset()


def serial_command(config: TargetConfig) -> CommandResult:
    return McuBackend(config).read_serial_log()


def run_command(config: TargetConfig, command_text: str) -> CommandResult:
    if config.type == "mcu":
        return CommandResult(
            command="run",
            ok=False,
            summary="MCU targets do not support shell command execution in this prototype.",
            details={
                "target_name": config.name,
                "target_type": config.type,
                "requested_command": command_text,
                "prototype_mode": True,
            },
        )
    if config.type != "linux-board":
        return CommandResult(
            command="run",
            ok=True,
            summary="Recorded intended command; remote execution is not implemented for this target type.",
            details={
                "target_name": config.name,
                "target_type": config.type,
                "requested_command": command_text,
                "workdir": config.runtime.get("workdir"),
                "prototype_mode": True,
            },
        )

    adapter = LinuxBoardAdapter(config)
    workdir = adapter.ensure_workdir()
    if not workdir.ok:
        return CommandResult(
            command="run",
            ok=False,
            summary="Failed to prepare remote workdir before execution.",
            details={
                "target_name": config.name,
                "requested_command": command_text,
                "workdir_check": _result_dict(workdir),
            },
        )

    remote = adapter.run(command_text)
    summary = "Remote command completed successfully." if remote.ok else "Remote command failed."
    details = {
        "target_name": config.name,
        "target_type": config.type,
        "requested_command": command_text,
        "workdir": config.runtime.get("workdir"),
        "workdir_check": _result_dict(workdir),
        "result": _result_dict(remote),
        "prototype_mode": False,
    }
    return CommandResult(command="run", ok=remote.ok, summary=summary, details=details)


def diagnose_command(bundle: str | Path) -> CommandResult:
    bundle_dir = Path(bundle).expanduser().resolve()
    manifest_path = bundle_dir / "manifest.json"
    if not bundle_dir.is_dir():
        return CommandResult(
            command="diagnose",
            ok=False,
            summary=f"Bundle directory does not exist: {bundle_dir}",
        )
    if not manifest_path.is_file():
        return CommandResult(
            command="diagnose",
            ok=False,
            summary=f"Bundle manifest is missing: {manifest_path}",
        )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    execution_state = manifest.get("execution_state", "unknown")
    classification = _classify_bundle(manifest)
    ok = execution_state in {"completed", "planned-only"}
    summary = (
        "Bundle looks valid and evidence collection completed."
        if execution_state == "completed"
        else f"Bundle inspection result: {classification}"
    )
    details = {
        "bundle_path": str(bundle_dir),
        "manifest_path": str(manifest_path),
        "classification": classification,
        "execution_state": execution_state,
        "next_step": _next_step_for_classification(classification),
    }
    return CommandResult(command="diagnose", ok=ok, summary=summary, details=details)


def _collect_planned_only(
    config: TargetConfig,
    bundle_dir: Path,
    target_snapshot: dict[str, object],
) -> CommandResult:
    manifest = {
        "created_at": now_iso(),
        "bundle_kind": "debugctl-evidence",
        "prototype_mode": True,
        "target_name": config.name,
        "target_type": config.type,
        "evidence_plan": [
            {"name": item, "command": EVIDENCE_COMMANDS.get(item, "<custom evidence>")}
            for item in config.evidence
        ],
        "execution_state": "planned-only",
    }
    write_json(bundle_dir / "target.json", target_snapshot)
    write_json(bundle_dir / "manifest.json", manifest)
    write_text(bundle_dir / "diagnosis.md", _diagnosis_markdown(manifest))
    write_text(
        bundle_dir / "run-summary.md",
        "\n".join(
            [
                "# Run Summary",
                "",
                f"- Target: `{config.name}`",
                f"- Type: `{config.type}`",
                f"- Evidence items: `{len(config.evidence)}`",
                "- Status: `planned-only`",
            ]
        ),
    )
    for index, item in enumerate(config.evidence, start=1):
        command_name = f"{index:02d}-{item}"
        write_text(
            bundle_dir / "commands" / f"{command_name}.stdout.txt",
            f"[planned] {EVIDENCE_COMMANDS.get(item, '<custom evidence>')}",
        )
        write_text(
            bundle_dir / "commands" / f"{command_name}.stderr.txt",
            "[prototype] remote execution not implemented",
        )
    return CommandResult(
        command="collect",
        ok=True,
        summary=f"Created prototype evidence bundle at {bundle_dir}",
        details={
            "bundle_path": str(bundle_dir),
            "evidence_items": config.evidence,
            "execution_state": "planned-only",
        },
        bundle_path=bundle_dir,
    )


def _collect_mcu(
    config: TargetConfig,
    bundle_dir: Path,
    target_snapshot: dict[str, object],
) -> CommandResult:
    backend = McuBackend(config)
    tool_status = backend.detect_tools()
    manifest = {
        "created_at": now_iso(),
        "bundle_kind": "debugctl-evidence",
        "prototype_mode": False,
        "target_name": config.name,
        "target_type": config.type,
        "execution_state": "tool-check",
        "tool_status": [asdict(tool) for tool in tool_status],
        "missing_tools": [tool.name for tool in tool_status if not tool.available],
    }
    write_json(bundle_dir / "target.json", target_snapshot)
    write_json(bundle_dir / "manifest.json", manifest)
    write_text(
        bundle_dir / "diagnosis.md",
        "\n".join(
            [
                "# Diagnosis",
                "",
                f"- Execution state: `tool-check`",
                f"- Missing tools: `{', '.join(manifest['missing_tools']) or 'none'}`",
                "- The MCU backend is wired but depends on host-side tools for flash/reset/serial.",
            ]
        ),
    )
    write_text(
        bundle_dir / "run-summary.md",
        "\n".join(
            [
                "# Run Summary",
                "",
                f"- Target: `{config.name}`",
                f"- Type: `{config.type}`",
                "- Status: `tool-check`",
            ]
        ),
    )
    return CommandResult(
        command="collect",
        ok=True,
        summary=f"Recorded MCU tool status bundle at {bundle_dir}",
        details={
            "bundle_path": str(bundle_dir),
            "tool_status": [asdict(tool) for tool in tool_status],
            "execution_state": "tool-check",
        },
        bundle_path=bundle_dir,
    )


def _diagnosis_markdown(manifest: dict[str, object]) -> str:
    lines = [
        "# Diagnosis",
        "",
        f"- Execution state: `{manifest.get('execution_state', 'unknown')}`",
        f"- Classification: `{_classify_bundle(manifest)}`",
    ]
    return "\n".join(lines)


def _classify_bundle(manifest: dict[str, object]) -> str:
    state = str(manifest.get("execution_state", "unknown"))
    if state == "completed":
        return "collection-complete"
    if state == "planned-only":
        return "prototype-no-remote-evidence"
    command_results = manifest.get("command_results")
    if isinstance(command_results, list):
        for item in command_results:
            if not isinstance(item, dict):
                continue
            returncode = item.get("returncode")
            if returncode == 255:
                return "ssh-connectivity-failure"
            if returncode == 127:
                return "missing-command-on-target"
            if isinstance(returncode, int) and returncode != 0:
                return "remote-command-failure"
    return "partial-evidence"


def _next_step_for_classification(classification: str) -> str:
    mapping = {
        "collection-complete": "Use the collected evidence or run a deeper board-specific diagnosis.",
        "prototype-no-remote-evidence": "Run collect against a linux-board target after SSH is configured.",
        "ssh-connectivity-failure": "Verify target reachability, SSH credentials, and BatchMode-compatible auth.",
        "missing-command-on-target": "Install the missing tool on the target or replace that evidence command.",
        "remote-command-failure": "Inspect the saved stdout/stderr files under commands/ for the failing evidence item.",
        "partial-evidence": "Review command_results in the manifest and inspect the failed command transcripts.",
    }
    return mapping.get(classification, "Inspect the manifest and command transcripts for more detail.")


def _result_dict(result: RemoteProcessResult | None) -> dict[str, object] | None:
    if result is None:
        return None
    return {
        "argv": result.argv,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
