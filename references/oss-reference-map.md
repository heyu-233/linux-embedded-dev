# OSS Reference Map

## Goal

Use this page to compare outside projects that inspired this skill, without copying their implementation directly.

## Reference Map

### labgrid

- **Borrow**
  - target/resource/driver separation
  - explicit board-facing resources
  - clean adapter boundaries for SSH, serial, and power
- **Do not adopt yet**
  - heavy framework dependency in the first CLI prototype
  - automatic orchestration before the basic evidence loop exists
- **Future use**
  - if power control, remote relays, or multi-resource orchestration becomes necessary

### tbot

- **Borrow**
  - host -> bootloader -> Linux shell workflow shape
  - stepwise automation for embedded bring-up
  - readable flow descriptions
- **Do not adopt yet**
  - tight coupling to a single workflow style
  - a larger abstraction surface before the core CLI stabilizes
- **Future use**
  - if we need repeatable scripted board sessions

### pytest-embedded

- **Borrow**
  - service/plugin style for serial, flash, and test backends
  - narrow backend interfaces
  - result classification by evidence
- **Do not adopt yet**
  - test-framework-first structure for a general debug tool
  - MCU-only assumptions in the Linux-board path
- **Future use**
  - for STM32F103 and other MCU targets

### AutoEmbed

- **Borrow**
  - closed-loop generation -> build -> flash/deploy -> verify
  - evidence-driven verification
- **Do not adopt yet**
  - LLM-centered orchestration before deterministic commands are stable
- **Future use**
  - as a higher-level planning layer on top of `debugctl`

### PlatformIO Core

- **Borrow**
  - board/build/upload vocabulary
  - backend selection idea
- **Do not adopt yet**
  - binding the whole project to one build system
- **Future use**
  - as one optional build backend for MCU targets

### Renode

- **Borrow**
  - simulation as a later-stage target class
  - separation between real hardware and emulated hardware
- **Do not adopt yet**
  - emulator integration in the first Linux-board prototype
- **Future use**
  - for MCU verification and repeatable CI loops

## Cross-Cutting Takeaway

The first version should stay small:

- one target profile
- one evidence bundle format
- one shell-safe execution path
- one clear output per command
