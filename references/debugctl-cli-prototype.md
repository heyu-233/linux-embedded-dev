# debugctl CLI Prototype

## Goal

Define the first CLI contract for the i.MX6ULL path before implementation details grow.

## Target Schema

```yaml
name: imx6ull
type: linux-board
connect:
  ssh: root@192.168.1.100
  serial: COM3
build:
  mode: local
deploy:
  method: scp
runtime:
  workdir: /tmp/embedded-agent
evidence:
  - uname
  - dmesg_tail
  - dev_nodes
  - modules
  - disk
```

## Commands

```bash
debugctl status --target target.yaml
debugctl collect --target target.yaml --out .runtime/latest
debugctl deploy --target target.yaml --artifact ./build/hello
debugctl run --target target.yaml --cmd "./hello"
debugctl diagnose --bundle .runtime/latest
```

## Prototype Constraints

- start with SSH + SCP + bounded shell evidence
- serial is optional input, not a hard requirement
- do not integrate labgrid or tbot yet
- keep command names close to the target/resource idea from mature tools

## Evidence Bundle Contract

`collect` should create a bundle that can be inspected later without re-running the board:

- command stdout and stderr
- hashes for deployed artifacts
- target snapshot
- diagnosis summary

## Phase 1 Scope

- `status` should be read-only
- `collect` should assemble evidence only
- `deploy` should validate local and target artifact hashes
- `run` should preserve stdout, stderr, and exit code
- `diagnose` should classify SSH failure, deploy failure, permission failure, missing binary, and runtime crash
