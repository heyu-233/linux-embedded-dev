---
name: linux-embedded-dev
description: Use this skill when the user is learning, building, debugging, reviewing, or optimizing Linux embedded systems. It is a broad skill for Linux embedded development across board bringup, boot flow, device tree, kernel drivers, root filesystem, build systems, userspace services, profiling, and project learning notes. It also covers specialized camera work such as i.MX6ULL plus OV5640 plus V4L2 capture paths.
---

# Linux Embedded Dev

## Overview

This is a broad Linux embedded development skill for learning and doing real work. It is meant to be the parent skill for board bringup, source reading, debugging, driver analysis, system integration, performance tuning, and project note keeping.

The camera workflow is not a separate skill anymore. It now lives inside this skill as a camera companion module, so Linux embedded bringup and media-specific debugging stay in one place.

## What To Borrow From Embedded Review

The `embedded-review` repository is useful as a design reference for structure:

- one clear top-level workflow instead of scattered advice
- references split by topic so the main skill stays lean
- practical, evidence-first review mindset
- checklists for high-risk areas instead of vague best practices

Use that same style here, but target Linux embedded work rather than MCU-only firmware review.

## Core Workflow

1. Identify the layer.
   - Decide whether the user is stuck in boot, kernel, device tree, driver probe, userspace integration, performance, or long-term maintenance.
   - If a codebase is available, locate the exact files before offering fixes.
2. Build the system path.
   - Map the real data or control path end to end.
   - For example: boot ROM -> bootloader -> kernel -> DTB -> driver probe -> device node -> userspace service or app.
3. Separate learning from fixing.
   - If the user wants to learn, prefer source-reading order, mental model, and checkpoints.
   - If the user wants to fix a bug, collect logs, config, topology, and reproduction steps first.
4. Inspect the ownership boundaries.
   - Track who owns clocks, regulators, resets, memory, buffers, interrupts, and state transitions.
   - Many Linux embedded bugs are ownership bugs, ordering bugs, or integration bugs rather than algorithm bugs.
5. Measure before optimizing.
   - Use profiling and observability tools before proposing structural changes.
   - Treat performance ideas as hypotheses that need evidence.
6. Record durable progress.
   - When a milestone, hard bug, or meaningful experiment finishes, update the single project-local learning note.

## Subdomains

- Boot and bringup
  - boot flow, kernel boot args, init, rootfs, driver probe order
- Device tree and hardware description
  - clocks, GPIO, regulators, pinctrl, buses, endpoints
- Kernel driver reading and review
  - probe, remove, PM, IRQ, DMA, locking, state machines
- Userspace integration
  - `/dev` nodes, daemons, service startup, test tools, IPC, app bringup
- Performance and observability
  - CPU, memory, wakeups, scheduler, copy paths, latency, throughput
- Camera and media
  - V4L2, media graph, sensor bringup, BSP versus upstream behavior
- Project notes and learning accumulation
  - one durable note file per project by default

## Camera Companion

Treat camera work as a companion module inside this broader skill:

- start from the Linux embedded layer first: booted system, DT wiring, probe path, device node creation
- then switch into camera-specific references for V4L2, media topology, sensor bringup, and capture-loop optimization
- keep camera notes in the same project-local learning note rather than splitting them into a separate camera-only skill

## Which Reference To Load

- For fast module routing, read `references/module-index.md` first.
- For a broad learning path and topic selection, read `references/linux-embedded-learning-roadmap.md`.
- For general source-reading and bringup flow, read `references/linux-embedded-debug-workflow.md`.
- For bootloader-to-kernel startup learning, read `references/boot-chain-and-startup.md`.
- For common bus debugging across I2C, SPI, UART, and MMC, read `references/common-bus-debugging.md`.
- For character device and platform driver study paths, read `references/char-device-and-platform-driver-path.md`.
- For device tree, probe, and driver ownership questions, read `references/device-tree-and-driver-workflow.md`.
- For root filesystem, build system, and userspace integration topics, read `references/build-rootfs-userspace.md`.
- For profiling and optimization across Linux embedded projects, read `references/perf-and-observability.md`.
- For project-local learning notes, milestone logs, and reusable templates, read `references/project-learning-note.md`.
- For camera-specific work, start with `references/camera-companion-index.md` and then load the linked camera references.

## Working Style

- Stay practical and identify the exact Linux layer before recommending changes.
- If the right layer is unclear, use the module index decision tree first and explicitly say which module you are entering.
- Default first response format:
  - I think you are currently at this layer or module.
  - I think so because of these clues.
  - The smallest useful next step is this.
  - After you do it, send me these exact results.
- Prefer source-reading order and checkpoints when the user is learning.
- Prefer logs, commands, and code locations when the user is debugging.
- Keep shell guidance incremental: give the smallest useful next step, wait for feedback, then continue.
- Maintain at most one project-local learning note by default. The default note path is `./linux-camera-learning-notes.md` unless the user asks for a different name.
- When normalizing a note, initialize reusable templates under `Hard Problems` and `Optimization Log`.
- On Windows, never write Chinese project-note content through a PowerShell inline here-string when the body contains non-ASCII text.
- Prefer direct file edits such as `apply_patch` for Chinese notes on Windows.
- After every Chinese note write on Windows, re-read the file and verify expected Chinese markers still exist before treating the write as successful.

## Review Mindset

When doing review, borrow the strongest habit from `embedded-review`: findings must be grounded in evidence and impact.

- Lead with correctness and system risks, not style.
- Call out ordering bugs, missing cleanup, incorrect ownership transfer, lifetime mismatches, and poor failure handling.
- For performance review, name the likely bottleneck, the evidence path, and the safest next validation step.
- Be explicit about what is known, what is inferred, and what still needs measurement.

## Example Requests

- "Help me learn Linux embedded development from bootloader to driver to userspace."
- "Guide me through reading this BSP kernel and device tree."
- "Explain the bootloader to kernel to init startup chain on this board."
- "Help me debug an I2C or SPI device that probes inconsistently."
- "Teach me the learning path for platform drivers and character devices."
- "Review this driver probe path and explain what owns clocks, GPIO, and regulators."
- "Help me debug why `/dev` node creation fails after probe succeeds."
- "Profile this Linux embedded app and suggest the highest-impact optimizations."
- "Analyze an i.MX6ULL plus OV5640 capture path and help me optimize V4L2 userspace code."
