# linux-embedded-dev

A Codex skill for Linux embedded learning, bringup, debugging, source reading, and performance work.

This skill is designed as a broad Linux embedded development companion rather than a narrow single-topic helper. It helps route problems by layer, guide source reading, structure debugging, and accumulate durable project notes.

It also includes a built-in camera companion module for media and V4L2 work such as i.MX6ULL + OV5640 bringup and capture-path analysis.

## What this skill covers

- Linux embedded learning roadmap
- Boot chain and startup analysis
- Device tree and driver workflow
- Common bus debugging
  - I2C
  - SPI
  - UART
  - MMC/SD
- Character device and platform driver learning path
- Root filesystem and userspace integration
- Profiling and observability
- Project-local learning notes
- Camera companion
  - V4L2
  - media graph
  - sensor bringup
  - capture-path optimization

## Skill structure

```text
linux-embedded-dev/
|-- SKILL.md
|-- README.md
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
    |-- project-learning-note.md
    |-- camera-companion-index.md
    `-- ...
```

## How it works

1. Route to the right module first.
2. Explain why that layer is the right entry point.
3. Give the smallest useful next step.
4. Ask the user to return the exact output needed for the next branch.

## Default response pattern

- I think you are currently at this layer or module.
- I think so because of these clues.
- The smallest useful next step is this.
- After you do it, send me these exact results.

## Camera companion

Camera work is included as a companion module inside the broader Linux embedded skill.

Current camera references are especially useful for i.MX6ULL + OV5640 style BSP workflows, but the structure is reusable for other Linux camera stacks too.

## Installation

Place this folder inside your local Codex skills directory.

Typical local location on Windows:

```text
C:\Users\<your-user>\.codex\skills\linux-embedded-dev
```

## Example prompts

- `Use $linux-embedded-dev to help me learn Linux embedded development from bootloader to userspace.`
- `Use $linux-embedded-dev to debug why my device tree node probes but no /dev node appears.`
- `Use $linux-embedded-dev to guide me through an I2C peripheral bringup.`
- `Use $linux-embedded-dev to explain the learning path for platform drivers and char devices.`
- `Use $linux-embedded-dev to analyze an i.MX6ULL + OV5640 V4L2 capture path.`
