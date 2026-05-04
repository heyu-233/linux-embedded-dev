from __future__ import annotations

import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from debugctl.models import CommandResult, TargetConfig, ToolStatus


@dataclass(slots=True)
class McuBackend:
    config: TargetConfig

    def status(self) -> CommandResult:
        tools = self.detect_tools()
        missing = [tool.name for tool in tools if not tool.available]
        ok = not missing
        return CommandResult(
            command="status",
            ok=ok,
            summary=(
                f"MCU toolchain is ready for '{self.config.name}'."
                if ok
                else f"MCU target '{self.config.name}' is missing required tools."
            ),
            details={
                "target_name": self.config.name,
                "target_type": self.config.type,
                "tool_status": [asdict(tool) for tool in tools],
                "missing_tools": missing,
                "prototype_mode": False,
            },
        )

    def flash(self, artifact: str | Path) -> CommandResult:
        artifact_path = Path(artifact).expanduser().resolve()
        if not artifact_path.is_file():
            return CommandResult(
                command="flash",
                ok=False,
                summary=f"Firmware artifact does not exist: {artifact_path}",
            )

        method = str(self.config.flash.get("method", "")).lower()
        if method == "openocd":
            return self._flash_with_openocd(artifact_path)
        if method == "st-flash":
            return self._flash_with_st_flash(artifact_path)
        return CommandResult(
            command="flash",
            ok=False,
            summary=f"Unsupported MCU flash method: {method or '<missing>'}",
            details={"method": method},
        )

    def reset(self) -> CommandResult:
        tools = self.detect_tools()
        openocd = self._tool_by_name(tools, "openocd")
        if openocd is None or not openocd.available:
            return CommandResult(
                command="reset",
                ok=False,
                summary="OpenOCD is required for reset in this prototype.",
                details={"missing_tools": [tool.name for tool in tools if not tool.available]},
            )
        return self._run_command(
            ["openocd", "-f", "interface/stlink.cfg", "-f", "target/stm32f1x.cfg", "-c", "init; reset; shutdown"],
            "reset",
        )

    def read_serial_log(self) -> CommandResult:
        serial_port = str(self.config.connect["serial"])
        pyserial = self._pyserial_status()
        if not pyserial.available:
            return CommandResult(
                command="read-serial",
                ok=False,
                summary="pyserial is required to read MCU serial logs in this prototype.",
                details={
                "serial_port": serial_port,
                "missing_tools": [pyserial.name],
                "tool_status": [asdict(pyserial)],
            },
        )
        return CommandResult(
            command="read-serial",
            ok=True,
            summary="Serial log support is wired in, but the capture loop is not yet implemented.",
            details={"serial_port": serial_port, "prototype_mode": True},
        )

    def detect_tools(self) -> list[ToolStatus]:
        return [
            self._tool_status("openocd"),
            self._tool_status("st-flash"),
            self._pyserial_status(),
        ]

    def _flash_with_openocd(self, artifact_path: Path) -> CommandResult:
        binary = artifact_path.as_posix()
        script = f"program {binary} verify reset exit"
        return self._run_command(
            ["openocd", "-f", "interface/stlink.cfg", "-f", "target/stm32f1x.cfg", "-c", script],
            "flash",
        )

    def _flash_with_st_flash(self, artifact_path: Path) -> CommandResult:
        return self._run_command(["st-flash", "--reset", "write", str(artifact_path), "0x8000000"], "flash")

    def _run_command(self, argv: list[str], command_name: str) -> CommandResult:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            check=False,
        )
        ok = completed.returncode == 0
        return CommandResult(
            command=command_name,
            ok=ok,
            summary=f"{command_name.capitalize()} command {'succeeded' if ok else 'failed'}.",
            details={
                "argv": argv,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "prototype_mode": False,
            },
        )

    def _tool_status(self, name: str) -> ToolStatus:
        path = shutil.which(name)
        if not path:
            return ToolStatus(name=name, available=False, note="not on PATH")
        version = self._version_for(name, path)
        return ToolStatus(name=name, available=True, path=path, version=version)

    def _pyserial_status(self) -> ToolStatus:
        try:
            import serial  # type: ignore
        except Exception:
            return ToolStatus(name="pyserial", available=False, note="pyserial not installed")
        return ToolStatus(name="pyserial", available=True, note=f"pyserial {getattr(serial, '__version__', 'installed')}")

    def _version_for(self, name: str, path: str) -> str | None:
        try:
            completed = subprocess.run([path, "--version"], capture_output=True, text=True, check=False)
        except Exception:
            return None
        text = (completed.stdout or completed.stderr or "").strip()
        return text.splitlines()[0] if text else None

    def _tool_by_name(self, tools: list[ToolStatus], name: str) -> ToolStatus | None:
        for tool in tools:
            if tool.name == name:
                return tool
        return None
