# linux-embedded-dev

A Codex skill for Linux embedded learning, bringup, debugging, source reading, review, and performance work.

`linux-embedded-dev` is designed as a broad Linux embedded development companion rather than a narrow single-topic helper. It routes problems by layer, guides source reading, keeps debugging incremental, and helps maintain durable project notes.

It also includes a camera companion module for media and V4L2 work, including i.MX6ULL + OV5640 bringup and capture-path analysis.

## Contents

- [What It Covers](#what-it-covers)
- [How It Works](#how-it-works)
- [Skill Structure](#skill-structure)
- [Installation](#installation)
- [Example Prompts](#example-prompts)
- [Design Notes](#design-notes)
- [License](#license)

## What It Covers

- Linux embedded learning roadmap
- Boot chain and startup analysis
- Device tree and driver workflow
- Common bus debugging: I2C, SPI, UART, MMC/SD
- Character device and platform driver learning path
- Root filesystem and userspace integration
- Profiling and observability
- Project-local learning notes
- Camera companion: V4L2, media graph, sensor bringup, capture-path optimization

## How It Works

The skill first routes the problem to the right Linux embedded layer, then gives a small next step and asks for the exact result needed for the next branch.

Default response shape:

```text
I think you are currently at this layer or module.
I think so because of these clues.
The smallest useful next step is this.
After you do it, send me these exact results.
```

This keeps debugging focused and avoids long command dumps before the system state is known.

## Skill Structure

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
    |-- project-learning-note.md
    |-- camera-companion-index.md
    `-- ...
```

## Key References

- `references/module-index.md`: first-stop decision tree for routing to boot, DT/driver, bus, userspace, performance, or camera work.
- `references/boot-chain-and-startup.md`: bootloader to kernel to init startup path.
- `references/device-tree-and-driver-workflow.md`: DTS, probe, ownership, and driver resource flow.
- `references/common-bus-debugging.md`: I2C, SPI, UART, and MMC/SD debug workflow.
- `references/char-device-and-platform-driver-path.md`: learning path for platform drivers and char-device style interfaces.
- `references/camera-companion-index.md`: entry point for V4L2, media graph, sensor bringup, and camera performance topics.

## Installation

Clone or download this repository, then place the folder in your local Codex skills directory.

Typical Windows location:

```text
C:\Users\<your-user>\.codex\skills\linux-embedded-dev
```

Typical Unix-like location:

```text
~/.codex/skills/linux-embedded-dev
```

## Example Prompts

```text
Use $linux-embedded-dev to help me learn Linux embedded development from bootloader to userspace.
```

```text
Use $linux-embedded-dev to debug why my device tree node probes but no /dev node appears.
```

```text
Use $linux-embedded-dev to guide me through an I2C peripheral bringup.
```

```text
Use $linux-embedded-dev to explain the learning path for platform drivers and char devices.
```

```text
Use $linux-embedded-dev to analyze an i.MX6ULL + OV5640 V4L2 capture path.
```

## Design Notes

This skill borrows structural ideas from embedded review workflows: a clear top-level workflow, topic-focused references, checklist-driven debugging, and evidence-first reasoning.

It is intentionally Linux-focused. MCU and RTOS firmware review patterns are useful inspiration, but this skill centers on Linux boot flow, device tree, drivers, userspace integration, and observability.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
