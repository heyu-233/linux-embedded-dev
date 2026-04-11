# Module Index

## Goal

Use this index first when the right Linux embedded submodule is not obvious. It is a fast routing layer for deciding whether to focus on boot, DT and driver, bus debugging, userspace integration, or the camera companion.

## Quick Decision Tree

### 1. Start with the symptom

- If the board does not boot, reboots early, hangs before shell, or fails around kernel handoff:
  - go to `boot-chain-and-startup.md`
- If the hardware exists on the board but Linux does not describe or initialize it correctly:
  - go to `device-tree-and-driver-workflow.md`
- If the problem looks like communication on `I2C`, `SPI`, `UART`, or `MMC`:
  - go to `common-bus-debugging.md`
- If probe succeeds but `/dev` nodes, services, or applications still fail:
  - go to `build-rootfs-userspace.md`
- If the device is camera, sensor, media graph, V4L2, or frame pipeline related:
  - go to `camera-companion-index.md`
- If the user wants to learn general driver structure, especially platform or char drivers:
  - go to `char-device-and-platform-driver-path.md`
- If the system works but CPU, latency, or throughput is bad:
  - go to `perf-and-observability.md`

### 2. Use the strongest first clue

Choose the module by the first concrete failure boundary, not by the most visible surface symptom.

Examples:

- "No `/dev/video1`" may still be a DT or probe problem before it is a userspace problem.
- "App open failed" may actually be boot order, permissions, or service startup.
- "Camera frame rate is bad" may be camera companion first, then perf and observability.
- "Sensor probe failed on I2C" usually starts in bus debugging plus DT and driver workflow.

### 3. Preferred combinations

Some problems naturally span two modules:

- boot + userspace
  - board boots to kernel, but service init fails
- DT and driver + bus debugging
  - node exists, but bus communication is unstable
- DT and driver + camera companion
  - sensor endpoint, clocks, reset, and V4L2 capture path all matter
- camera companion + perf and observability
  - functional capture works, but CPU or frame rate is poor

## Recommended Response Pattern

When using this index, respond in this style:

- state which layer or module you think the user is currently in
- explain why you think so
- give the smallest useful next step
- ask the user to send back the exact result needed for the next branch

Example:

- "I think you are currently in the DT/driver layer."
- "I think so because the board sees the hardware but Linux is not exposing the expected node."
- "The smallest useful next step is to inspect the DTS node and probe log."
- "After you do that, send me the DTS snippet and the relevant `dmesg` lines."
