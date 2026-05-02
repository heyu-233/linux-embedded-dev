# Full-Link Debug Pipeline

## Goal

Use this reference when a Linux embedded project needs a host-side command line pipeline that can build, deploy, restart, and inspect an end-to-end system spanning a host PC, a build VM, an embedded board, backend services, frontend services, message middleware, and logs.

The pattern is based on a real IoT edge-device workflow, but all project-specific names, IP addresses, user names, local paths, and key names are intentionally replaced with placeholders.

## Architecture Pattern

```text
[Host PC / Codex terminal]
    |
    |-- SSH --> [Build VM: <vm-host>]
    |              cross toolchain
    |              vendor kernel source
    |              target-matched headers and libraries
    |
    |-- SSH --> [Embedded board: <board-host>]
    |              target runtime libraries
    |              BusyBox shell
    |              device test tools
    |              edge agent
    |
    `-- local --> [Backend + frontend + reverse proxy + database]
                   project root: <project-root>
```

## What This Solves

- one terminal can inspect every layer
- build and deploy steps become repeatable
- board logs, backend logs, and service state are checked from one place
- debugging shifts from manual guessing to staged health checks
- AI-assisted debugging gets concrete command outputs instead of broad descriptions

## SSH Access Pattern

Use SSH aliases rather than raw IP addresses in every command.

Example `~/.ssh/config` shape:

```sshconfig
Host build-vm
  HostName <vm-host>
  User <vm-user>
  IdentityFile <path-to-build-vm-key>

Host board
  HostName <board-host>
  User <board-user>
  IdentityFile <path-to-board-key>
  BindAddress <host-board-ip>
  StrictHostKeyChecking accept-new
```

`BindAddress` is important when the host has multiple network interfaces in the same subnet. It forces SSH traffic to leave through the interface connected to the board.

## Multi-NIC ARP Conflict Check

Symptoms:

- `ping <board-host>` works, but SSH or TCP connections fail
- the board cannot ping the host
- `arp -a` shows confusing or duplicate board entries

Useful host-side check:

```powershell
arp -a | findstr "<board-host>"
```

If two host interfaces appear to know the board address, use an SSH alias with `BindAddress <host-board-ip>` or fix the host routing table.

## Toolchain Compatibility Matrix

Keep a small matrix for target ABI compatibility.

```text
component              target runtime       build side
compiler               n/a                  <vendor-matched-gcc>
libc                   <target-libc>         linked by matched toolchain
third-party headers    target ABI version    matching source release
third-party .so libs   target ABI version    copied from board or sysroot
```

Why this matters:

- a modern distro cross compiler may emit binaries requiring a newer `glibc` than the board has
- headers from a newer library release may compile successfully but crash against older target `.so` files
- silent exits can be ABI mismatch, not application logic

## Binary Transfer Pattern

When `scp` is unreliable or unavailable, use a base64 SSH pipe.

```powershell
ssh build-vm "cat <remote-binary-path>" > .runtime\artifact.bin
certutil -encode .runtime\artifact.bin .runtime\artifact.b64 | Out-Null
Get-Content .runtime\artifact.b64 | ssh board "base64 -d > <target-binary-path> && chmod +x <target-binary-path>"
```

On Unix-like hosts:

```bash
ssh build-vm "cat <remote-binary-path>" > /tmp/artifact.bin
base64 /tmp/artifact.bin | ssh board "base64 -d > <target-binary-path> && chmod +x <target-binary-path>"
```

Add checksum verification when possible:

```bash
sha256sum /tmp/artifact.bin
ssh board "sha256sum <target-binary-path>"
```

## Clean Board Restart Pattern

For BusyBox systems without `systemd`, keep restart explicit and idempotent.

```bash
ssh board "killall -9 <agent-process> <stream-process> <subscriber-process> 2>/dev/null"
ssh board "rm -f /tmp/<agent>.lock"
ssh board "nohup <start-script> > /dev/null 2>&1 &"
ssh board "ps | grep -E '<agent>|<stream>|<subscriber>' | grep -v grep"
```

If the board starts the agent from `rcS`, guard the start script with a lock file and stale-PID cleanup.

## Host-Side Status Command

Create one host-side command that performs read-only checks across the whole chain.

Example shape:

```powershell
.\scripts\debugctl.ps1 status
```

Recommended checks:

- backend, frontend, proxy, and message-broker ports
- backend health endpoint
- PID files for locally managed processes
- build VM SSH
- board SSH
- board process list
- board device nodes
- board-to-host message publish
- board boot or agent log tails
- local backend, frontend, and detector log tails

The status command should not restart services or modify board state. It should only report the current health of the chain.

## Log Map

Keep a table of log locations and bounded commands.

```text
layer                  location                         command
board boot             <board-boot-log>                 ssh board "tail -30 <board-boot-log>"
board agent            <board-agent-log>                ssh board "tail -30 <board-agent-log>"
board stream           <board-stream-log>               ssh board "tail -30 <board-stream-log>"
backend stdout         .runtime/logs/backend.out.log    Get-Content ... -Tail 30
backend stderr         .runtime/logs/backend.err.log    Get-Content ... -Tail 30
frontend stdout        .runtime/logs/frontend.out.log   Get-Content ... -Tail 30
```

Always request bounded log output unless full logs are truly required.

## Security Notes

- Use separate SSH keys for VM and board when practical.
- Avoid publishing real IP addresses, usernames, local paths, SSH key filenames, or public keys in reusable docs.
- Passwordless keys are acceptable for a controlled development lab, but document that they are not a production security model.
- Do not commit private keys, project-specific credentials, database passwords, or raw `.ssh/config` files.

## How To Use This In A Skill Session

When a user says they have a host-side full-link debug pipeline:

1. Ask for or inspect the pipeline topology.
2. Identify the weakest manual step.
3. Prefer creating a read-only `status` command before build or deploy automation.
4. Add deployment checks such as file size and checksum after the status path is stable.
5. Record hard-won findings as a reusable note or case study, with private values replaced by placeholders.
