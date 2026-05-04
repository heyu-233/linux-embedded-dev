from __future__ import annotations

import argparse
import json
import sys

from debugctl.commands import (
    collect_command,
    deploy_command,
    diagnose_command,
    flash_command,
    reset_command,
    run_command,
    serial_command,
    status_command,
)
from debugctl.models import CommandResult
from debugctl.target import TargetConfigError, load_target_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="debugctl")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Inspect target configuration.")
    status_parser.add_argument("--target", required=True, help="Path to target.yaml")
    status_parser.set_defaults(handler=_handle_target_command)

    collect_parser = subparsers.add_parser("collect", help="Create a prototype evidence bundle.")
    collect_parser.add_argument("--target", required=True, help="Path to target.yaml")
    collect_parser.add_argument("--out", required=True, help="Output bundle directory")
    collect_parser.set_defaults(handler=_handle_target_command)

    deploy_parser = subparsers.add_parser("deploy", help="Validate a deploy artifact.")
    deploy_parser.add_argument("--target", required=True, help="Path to target.yaml")
    deploy_parser.add_argument("--artifact", required=True, help="Local artifact path")
    deploy_parser.set_defaults(handler=_handle_target_command)

    run_parser = subparsers.add_parser("run", help="Record an intended remote command.")
    run_parser.add_argument("--target", required=True, help="Path to target.yaml")
    run_parser.add_argument("--cmd", required=True, help="Command to execute remotely")
    run_parser.set_defaults(handler=_handle_target_command)

    flash_parser = subparsers.add_parser("flash", help="Flash an MCU target artifact.")
    flash_parser.add_argument("--target", required=True, help="Path to target.yaml")
    flash_parser.add_argument("--artifact", required=True, help="Firmware image path")
    flash_parser.set_defaults(handler=_handle_target_command)

    reset_parser = subparsers.add_parser("reset", help="Reset an MCU target.")
    reset_parser.add_argument("--target", required=True, help="Path to target.yaml")
    reset_parser.set_defaults(handler=_handle_target_command)

    serial_parser = subparsers.add_parser("serial", help="Read MCU serial log.")
    serial_parser.add_argument("--target", required=True, help="Path to target.yaml")
    serial_parser.set_defaults(handler=_handle_target_command)

    diagnose_parser = subparsers.add_parser("diagnose", help="Inspect an evidence bundle.")
    diagnose_parser.add_argument("--bundle", required=True, help="Path to bundle directory")
    diagnose_parser.set_defaults(handler=_handle_bundle_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = args.handler(args)
    except TargetConfigError as exc:
        _print_error(str(exc))
        return 2

    if result.ok:
        _print_result(result)
        return 0

    _print_result(result, stream=sys.stderr)
    return 1


def _handle_target_command(args: argparse.Namespace) -> CommandResult:
    config = load_target_config(args.target)
    if args.command == "status":
        return status_command(config)
    if args.command == "collect":
        return collect_command(config, args.out)
    if args.command == "deploy":
        return deploy_command(config, args.artifact)
    if args.command == "run":
        return run_command(config, args.cmd)
    if args.command == "flash":
        return flash_command(config, args.artifact)
    if args.command == "reset":
        return reset_command(config)
    if args.command == "serial":
        return serial_command(config)
    raise AssertionError(f"Unhandled target command: {args.command}")


def _handle_bundle_command(args: argparse.Namespace) -> CommandResult:
    return diagnose_command(args.bundle)


def _print_result(result: CommandResult, stream: object = sys.stdout) -> None:
    payload = {
        "command": result.command,
        "ok": result.ok,
        "summary": result.summary,
        "details": result.details,
    }
    if result.bundle_path:
        payload["bundle_path"] = str(result.bundle_path)
    print(json.dumps(payload, indent=2, sort_keys=True), file=stream)


def _print_error(message: str) -> None:
    payload = {"ok": False, "error": message}
    print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
