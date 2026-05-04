from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from debugctl.models import TargetConfig


@dataclass(slots=True)
class RemoteProcessResult:
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


Executor = Callable[..., subprocess.CompletedProcess[str]]


class LinuxBoardAdapter:
    def __init__(self, config: TargetConfig, executor: Executor | None = None) -> None:
        self.config = config
        self.executor = executor or subprocess.run
        self.host = str(config.connect["ssh"])
        self.timeout = int(config.runtime.get("timeout_sec", 30))

    def probe(self) -> RemoteProcessResult:
        return self.run("printf 'debugctl-ok\\n'", use_workdir=False)

    def ensure_workdir(self) -> RemoteProcessResult:
        workdir = self._remote_workdir()
        return self.run(f"mkdir -p {shlex.quote(workdir)}", use_workdir=False)

    def run(self, command_text: str, use_workdir: bool = True) -> RemoteProcessResult:
        remote_command = command_text
        if use_workdir:
            workdir = shlex.quote(self._remote_workdir())
            remote_command = f"cd {workdir} && {command_text}"

        wrapped = f"sh -lc {shlex.quote(remote_command)}"
        argv = [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={self.timeout}",
            self.host,
            wrapped,
        ]
        return self._invoke(argv)

    def copy_to(self, local_path: str | Path, remote_path: str) -> RemoteProcessResult:
        argv = [
            "scp",
            "-o",
            "BatchMode=yes",
            "-o",
            f"ConnectTimeout={self.timeout}",
            str(Path(local_path).expanduser().resolve()),
            f"{self.host}:{remote_path}",
        ]
        return self._invoke(argv)

    def read_remote_sha256(self, remote_path: str) -> RemoteProcessResult:
        script = "\n".join(
            [
                f"target={shlex.quote(remote_path)}",
                "if command -v sha256sum >/dev/null 2>&1; then",
                "  sha256sum \"$target\" | awk '{print $1}'",
                "elif command -v shasum >/dev/null 2>&1; then",
                "  shasum -a 256 \"$target\" | awk '{print $1}'",
                "elif command -v python3 >/dev/null 2>&1; then",
                "  python3 - \"$target\" <<'PY'",
                "import hashlib",
                "import pathlib",
                "import sys",
                "path = pathlib.Path(sys.argv[1])",
                "print(hashlib.sha256(path.read_bytes()).hexdigest())",
                "PY",
                "else",
                "  echo 'No SHA-256 tool available on target' >&2",
                "  exit 127",
                "fi",
            ]
        )
        return self.run(script, use_workdir=False)

    def _remote_workdir(self) -> str:
        return str(self.config.runtime["workdir"])

    def _invoke(self, argv: list[str]) -> RemoteProcessResult:
        completed = self.executor(
            argv,
            capture_output=True,
            text=True,
            check=False,
            timeout=self.timeout,
        )
        return RemoteProcessResult(
            argv=argv,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
