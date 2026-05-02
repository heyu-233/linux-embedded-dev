# linux-embedded-dev

> A Codex skill for Linux embedded bring-up, driver reading, board debugging, full-link diagnostics, and practical learning.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827.svg)](SKILL.md)
[![Focus](https://img.shields.io/badge/Focus-Linux%20Embedded-0f766e.svg)](#what-it-helps-with)
[![Camera Companion](https://img.shields.io/badge/Module-V4L2%20%2F%20Camera-7c3aed.svg)](references/camera-companion-index.md)

`linux-embedded-dev` turns Codex into a structured Linux embedded development partner. It helps you move from scattered logs, device-tree fragments, shell commands, and driver code into a clear debugging path:

```text
identify the layer -> ask for bounded evidence -> explain the system role -> take the next smallest step -> record what was learned
```

It is built for real embedded work: vendor BSPs, old toolchains, DTS bring-up, `/dev` node mysteries, cross-compilation, rootfs integration, V4L2 camera paths, board-side scripts, and host-side full-link debug pipelines.

## Why This Exists

Embedded Linux debugging is rarely one clean problem. A camera issue may actually be a device-tree endpoint issue. A userspace failure may be a probe-path issue. A "works on the host" binary may fail because of `glibc` or library ABI mismatch.

This skill gives Codex a reusable operating style for that world:

- route the issue to the right layer first
- teach the mental model without dumping a lecture
- ask for small command outputs instead of giant logs
- map DTS, driver, board, and userspace artifacts together
- keep hard-won project knowledge in reusable notes

## What It Helps With

- Board bring-up and boot-chain debugging
- Device tree, DTS, clocks, GPIO, regulators, reset, and pinctrl
- Kernel driver and platform-code reading
- Character device and platform driver learning paths
- I2C, SPI, UART, MMC/SD bus debugging
- Cross-compilation and target ABI compatibility
- Root filesystem and userspace integration
- Service startup, `/dev` nodes, logs, and process supervision
- Performance and observability with bounded evidence
- V4L2, media graph, sensor bring-up, and capture-path optimization
- Host-to-VM-to-board full-link debug pipelines

## Quickstart

Clone this repository into your Codex skills directory.

```powershell
git clone https://github.com/heyu-233/linux-embedded-dev `
  C:\Users\<your-user>\.codex\skills\linux-embedded-dev
```

Unix-like systems:

```bash
git clone https://github.com/heyu-233/linux-embedded-dev \
  ~/.codex/skills/linux-embedded-dev
```

Then invoke it explicitly:

```text
Use $linux-embedded-dev to debug why my DTS node probes but no /dev node appears.
```

## The Default Working Loop

The skill is designed to keep each turn executable and small:

```text
Mode: teaching or efficiency
Current goal: what this turn is trying to confirm
Principle in brief: where this step sits in the system
Do this now: one command, one file, or one minimal edit
Send back: the exact output needed for the next branch
```

That loop is especially useful when working with a physical board, because every extra manual step costs time and every huge log dump creates noise.

## Module Map

Start with `references/module-index.md` when the right layer is unclear.

| If the symptom looks like... | Start here |
|---|---|
| board does not boot, hangs early, bad bootargs | `references/boot-chain-and-startup.md` |
| hardware exists but Linux does not bind it correctly | `references/device-tree-and-driver-workflow.md` |
| I2C, SPI, UART, or MMC communication is unstable | `references/common-bus-debugging.md` |
| probe succeeds but userspace still fails | `references/build-rootfs-userspace.md` |
| learning platform drivers or char devices | `references/char-device-and-platform-driver-path.md` |
| CPU, latency, frame rate, throughput, or stability | `references/perf-and-observability.md` |
| camera, V4L2, media graph, sensor bring-up | `references/camera-companion-index.md` |
| host terminal controls VM, board, backend, logs | `references/full-link-debug-pipeline.md` |

## Repository Structure

```text
linux-embedded-dev/
|-- SKILL.md
|-- README.md
|-- LICENSE
|-- agents/
|   `-- openai.yaml
`-- references/
    |-- module-index.md
    |-- linux-embedded-learning-roadmap.md
    |-- linux-embedded-debug-workflow.md
    |-- boot-chain-and-startup.md
    |-- device-tree-and-driver-workflow.md
    |-- common-bus-debugging.md
    |-- char-device-and-platform-driver-path.md
    |-- build-rootfs-userspace.md
    |-- perf-and-observability.md
    |-- full-link-debug-pipeline.md
    |-- project-learning-note.md
    |-- camera-companion-index.md
    `-- ...
```

## Example Prompts

```text
Use $linux-embedded-dev to help me understand this i.MX6ULL boot log.
```

```text
Use $linux-embedded-dev to build a code map for this platform driver.
```

```text
Use $linux-embedded-dev to debug an I2C sensor that sometimes probes and sometimes fails.
```

```text
Use $linux-embedded-dev to design a host-side full-link debug pipeline for my board.
```

```text
Use $linux-embedded-dev to analyze an OV5640 + V4L2 capture path and reduce CPU usage.
```

## Camera Companion

Camera work is included as a companion module rather than a separate skill. The goal is to keep Linux bring-up context and media-specific debugging in the same reasoning path.

Useful camera references:

- `references/camera-companion-index.md`
- `references/imx6ull-camera-pipeline.md`
- `references/ov5640-bringup-checklist.md`
- `references/v4l2-buffer-lifecycle.md`
- `references/perf-tuning-checklist.md`
- `references/profiling-playbook.md`

## Full-Link Debug Pipeline

The skill includes a sanitized pattern for projects where one host terminal controls the whole chain:

```text
Host PC -> build VM -> embedded board -> backend/frontend/proxy/database -> logs
```

See `references/full-link-debug-pipeline.md` for a reusable template covering SSH aliases, multi-NIC routing issues, target ABI checks, base64 SSH deployment, board restart patterns, status commands, and log maps.

## Design Principles

- **Layer first**: boot, DTS, driver, bus, userspace, performance, or camera.
- **Evidence before advice**: logs, commands, file paths, callbacks, and exact symptoms.
- **Small steps**: one meaningful command or edit at a time by default.
- **Teach while debugging**: short explanations that build the user's mental model.
- **Reusable notes**: keep milestone, hard-problem, and optimization findings durable.
- **Privacy-aware case studies**: publish patterns, not raw personal lab details.

## Inspiration

This skill borrows the strongest structural habits from mature engineering READMEs and embedded review workflows: a crisp promise at the top, quick installation, concrete use cases, focused references, and evidence-first checklists.

It is intentionally focused on Linux embedded systems rather than MCU-only firmware. The center of gravity is boot flow, device tree, drivers, userspace integration, observability, and practical board work.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
