from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from debugctl.commands import collect_command, deploy_command, run_command, status_command
from debugctl.models import CommandResult, ToolStatus
from debugctl.mcu import McuBackend
from debugctl.target import TargetConfigError, load_target_config
from debugctl.transport import RemoteProcessResult

REPO_ROOT = Path(__file__).resolve().parents[1]


class TargetConfigTests(unittest.TestCase):
    def test_load_linux_board_example(self) -> None:
        config = load_target_config(REPO_ROOT / "examples" / "target.imx6ull.yaml")
        self.assertEqual(config.name, "imx6ull")
        self.assertEqual(config.type, "linux-board")
        self.assertEqual(config.connect["ssh"], "root@192.168.1.100")

    def test_reject_missing_linux_board_ssh(self) -> None:
        bad_target = REPO_ROOT / "tests" / "_bad_target.yaml"
        bad_target.write_text(
            "\n".join(
                [
                    "name: broken",
                    "type: linux-board",
                    "connect:",
                    "  serial: COM3",
                    "runtime:",
                    "  workdir: /tmp/test",
                    "evidence:",
                    "  - uname",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        self.addCleanup(bad_target.unlink)

        with self.assertRaises(TargetConfigError):
            load_target_config(bad_target)


class CommandTests(unittest.TestCase):
    def test_collect_creates_manifest_for_mcu_target(self) -> None:
        config = load_target_config(REPO_ROOT / "examples" / "target.stm32f103.yaml")
        with tempfile.TemporaryDirectory() as temp_dir:
            result = collect_command(config, temp_dir)
            manifest = Path(temp_dir) / "manifest.json"
            self.assertTrue(result.ok)
            self.assertTrue(manifest.is_file())
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["execution_state"], "tool-check")

    def test_collect_runs_remote_evidence_for_linux_board(self) -> None:
        config = load_target_config(REPO_ROOT / "examples" / "target.imx6ull.yaml")
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("debugctl.commands.LinuxBoardAdapter") as adapter_cls:
                adapter = adapter_cls.return_value
                adapter.ensure_workdir.return_value = RemoteProcessResult(
                    argv=["ssh"],
                    returncode=0,
                    stdout="",
                    stderr="",
                )
                adapter.run.side_effect = [
                    RemoteProcessResult(argv=["ssh"], returncode=0, stdout="Linux target\n", stderr=""),
                    RemoteProcessResult(argv=["ssh"], returncode=0, stdout="dmesg\n", stderr=""),
                    RemoteProcessResult(argv=["ssh"], returncode=0, stdout="/dev/null\n", stderr=""),
                    RemoteProcessResult(argv=["ssh"], returncode=0, stdout="module\n", stderr=""),
                    RemoteProcessResult(argv=["ssh"], returncode=0, stdout="disk\n", stderr=""),
                ]
                result = collect_command(config, temp_dir)

            manifest = Path(temp_dir) / "manifest.json"
            self.assertTrue(result.ok)
            self.assertTrue(manifest.is_file())
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["execution_state"], "completed")
            self.assertEqual(len(payload["command_results"]), 5)

    def test_deploy_rejects_missing_artifact(self) -> None:
        config = load_target_config(REPO_ROOT / "examples" / "target.imx6ull.yaml")
        result = deploy_command(config, REPO_ROOT / "tests" / "missing.bin")
        self.assertFalse(result.ok)

    def test_deploy_uploads_and_verifies_remote_hash(self) -> None:
        config = load_target_config(REPO_ROOT / "examples" / "target.imx6ull.yaml")
        artifact = REPO_ROOT / "tests" / "_artifact.bin"
        artifact.write_bytes(b"debugctl")
        self.addCleanup(artifact.unlink)

        with patch("debugctl.commands.LinuxBoardAdapter") as adapter_cls:
            adapter = adapter_cls.return_value
            adapter.ensure_workdir.return_value = RemoteProcessResult(
                argv=["ssh"],
                returncode=0,
                stdout="",
                stderr="",
            )
            adapter.copy_to.return_value = RemoteProcessResult(
                argv=["scp"],
                returncode=0,
                stdout="",
                stderr="",
            )
            adapter.read_remote_sha256.return_value = RemoteProcessResult(
                argv=["ssh"],
                returncode=0,
                stdout="b345898a0e0669b5ea7886abcce344d399727c7d51d09f72a8ec1c00ed5ed3cf\n",
                stderr="",
            )

            result = deploy_command(config, artifact)

        self.assertTrue(result.ok)
        self.assertIn("remote_artifact_sha256", result.details)

    def test_status_checks_connectivity_for_linux_board(self) -> None:
        config = load_target_config(REPO_ROOT / "examples" / "target.imx6ull.yaml")
        with patch("debugctl.commands.LinuxBoardAdapter") as adapter_cls:
            adapter = adapter_cls.return_value
            adapter.probe.return_value = RemoteProcessResult(
                argv=["ssh"],
                returncode=0,
                stdout="debugctl-ok\n",
                stderr="",
            )
            adapter.ensure_workdir.return_value = RemoteProcessResult(
                argv=["ssh"],
                returncode=0,
                stdout="",
                stderr="",
            )
            result = status_command(config)

        self.assertTrue(result.ok)
        self.assertEqual(result.details["probe"]["returncode"], 0)

    def test_run_executes_remote_command_for_linux_board(self) -> None:
        config = load_target_config(REPO_ROOT / "examples" / "target.imx6ull.yaml")
        with patch("debugctl.commands.LinuxBoardAdapter") as adapter_cls:
            adapter = adapter_cls.return_value
            adapter.ensure_workdir.return_value = RemoteProcessResult(
                argv=["ssh"],
                returncode=0,
                stdout="",
                stderr="",
            )
            adapter.run.return_value = RemoteProcessResult(
                argv=["ssh"],
                returncode=0,
                stdout="hello\n",
                stderr="",
            )
            result = run_command(config, "./hello")

        self.assertTrue(result.ok)
        self.assertEqual(result.details["result"]["stdout"], "hello\n")

    def test_mcu_status_reports_missing_tools(self) -> None:
        config = load_target_config(REPO_ROOT / "examples" / "target.stm32f103.yaml")
        with patch.object(
            McuBackend,
            "detect_tools",
            return_value=[
                ToolStatus(name="openocd", available=False, note="not on PATH"),
                ToolStatus(name="st-flash", available=False, note="not on PATH"),
                ToolStatus(name="pyserial", available=False, note="not installed"),
            ],
        ):
            result = McuBackend(config).status()

        self.assertFalse(result.ok)
        self.assertEqual(result.details["missing_tools"], ["openocd", "st-flash", "pyserial"])

    def test_mcu_flash_uses_selected_backend(self) -> None:
        config = load_target_config(REPO_ROOT / "examples" / "target.stm32f103.yaml")
        firmware = REPO_ROOT / "tests" / "_firmware.bin"
        firmware.write_bytes(b"firmware")
        self.addCleanup(firmware.unlink)

        with patch.object(McuBackend, "_run_command") as run_command:
            run_command.return_value = CommandResult(
                command="flash",
                ok=True,
                summary="Flash command succeeded.",
                details={"argv": ["openocd"], "returncode": 0},
            )
            result = McuBackend(config).flash(firmware)

        self.assertEqual(result.command, "flash")

    def test_mcu_reset_requires_openocd(self) -> None:
        config = load_target_config(REPO_ROOT / "examples" / "target.stm32f103.yaml")
        with patch.object(McuBackend, "detect_tools", return_value=[]):
            result = McuBackend(config).reset()

        self.assertFalse(result.ok)


class CliTests(unittest.TestCase):
    def test_status_command_emits_json(self) -> None:
        command = [
            sys.executable,
            "-m",
            "debugctl",
            "collect",
            "--target",
            str(REPO_ROOT / "examples" / "target.stm32f103.yaml"),
            "--out",
            str(REPO_ROOT / "tests" / "_bundle_cli"),
        ]
        bundle_dir = REPO_ROOT / "tests" / "_bundle_cli"
        self.addCleanup(lambda: bundle_dir.exists() and __import__("shutil").rmtree(bundle_dir))
        if bundle_dir.exists():
            if bundle_dir.is_dir():
                import shutil

                shutil.rmtree(bundle_dir)
            else:
                bundle_dir.unlink()
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env={**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "collect")

    def test_mcu_status_command_emits_json(self) -> None:
        command = [
            sys.executable,
            "-m",
            "debugctl",
            "status",
            "--target",
            str(REPO_ROOT / "examples" / "target.stm32f103.yaml"),
        ]
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env={**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 1, completed.stderr)
        payload = json.loads(completed.stdout or completed.stderr)
        self.assertEqual(payload["command"], "status")


if __name__ == "__main__":
    unittest.main()
