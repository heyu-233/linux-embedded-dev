# Debug Checklists

Use these checklists as compact prompts for investigation. Copy the relevant section into the working notes and fill in concrete evidence.

## Generic board bring-up

- board / SoC / kernel / vendor tree
- boot stage failing: ROM, bootloader, kernel, init, userspace
- clock / regulator / reset / pinmux dependencies
- DTS nodes and compatibles involved
- exact failing log lines
- last known good commit or image if available

## Driver probe failure

- matching DTS node and `compatible`
- driver `probe()` or subsystem registration path
- return code and first failing helper
- requested clocks, GPIOs, regulators, IRQs, memory regions
- whether the failure is permanent or `-EPROBE_DEFER`
- minimal test to validate the top hypothesis

## Build and integration

- toolchain version and target triple
- defconfig / fragment / Yocto layer involved
- out-of-tree patch set if any
- compile or link error line
- whether the module or builtin config is enabled
- artifact location: image, dtb, module, rootfs package

## Performance and stability

- workload definition: resolution, FPS, bitrate, stream count
- CPU, memory, and temperature snapshot
- when the regression starts
- logs around underrun, timeout, dropped frame, reset
- one variable to reduce first: resolution, FPS, format, pipeline depth
