# Agent Architecture Notes

## Goal

This page defines the design rules for the `debugctl` prototype and later agent runtime work.

## Design Rules

- `target` is not the same thing as a shell.
- `connection` must be a replaceable adapter, not a hard-coded transport.
- the evidence bundle is the primary output of the agent
- every artifact must be traceable back to a command, target, or classification step
- destructive actions must be staged and classified before execution

## Runtime Shape

The first runtime should produce a simple, inspectable bundle:

- `target.json`
- `manifest.json`
- `commands/*.stdout.txt`
- `commands/*.stderr.txt`
- `artifacts/*.sha256.txt`
- `diagnosis.md`
- `run-summary.md`

## Minimal Loop

1. plan
2. execute
3. collect
4. classify
5. record

## Output Principle

Prefer deterministic evidence over free-form narration. If a result can be stored as a file, hash, or command transcript, store it that way first.
