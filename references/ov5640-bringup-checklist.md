# OV5640 Bringup Checklist

## Goal

Use this checklist when the sensor does not probe, streams no frames, negotiates the wrong format, or behaves inconsistently across resets.

## 1. Basic Probe Checks

- Confirm the I2C bus number and address match the board design.
- Confirm the driver reads the expected chip ID during probe.
- Check that the external input clock is enabled before the sensor is accessed.
- Verify `reset` and `pwdn` polarity in DTS or board code.
- Confirm regulators or power rails are enabled in the correct order.

Typical failure signatures:

- I2C read errors during probe: often clock, power, address, or wiring.
- Unexpected chip ID: often wrong sensor, unstable power, or reset timing issue.
- Probe succeeds but stream-on fails: often mode setup, endpoint mismatch, or host-side format mismatch.

## 2. Mode and Format Sanity

- Confirm the sensor output format matches what the host side expects.
- Confirm width, height, and frame interval are supported by the active mode.
- Check if the BSP branch uses custom mode tables or branch-specific defaults.
- If frames are corrupted, verify bus width, synchronization polarity, and field order assumptions.

## 3. Streaming Checks

When probe succeeds but no image arrives:

- Verify stream-on actually programs the sensor registers for the selected mode.
- Confirm the capture host enables the receiver path and DMA before or at stream-on.
- Check whether interrupts are firing on frame completion.
- Confirm at least a few buffers were queued before `STREAMON`.
- Verify userspace is dequeuing and requeueing frames instead of stalling after the first buffer.

## 4. Reset and Powerdown Logic

OV5640 issues are often caused by reset sequencing mistakes rather than by V4L2 logic.

Check:

- active-high versus active-low interpretation for `reset`
- active-high versus active-low interpretation for `pwdn`
- delay durations between power, reset release, and I2C transactions
- whether the board code or bootloader left the sensor in an unexpected state

## 5. Debug Inputs To Gather

Before changing code, collect:

- `dmesg` lines for probe, format setup, and stream-on
- `v4l2-ctl --all` and `--list-formats-ext` output
- media topology from `media-ctl -p` when available
- the exact DTS snippet for sensor clocks, GPIOs, and endpoints
- whether a known-good test such as `yavta` or `v4l2-ctl --stream-mmap` can capture frames

## 6. Bringup Priority Order

Use this order to avoid chasing fake software problems:

1. power, clock, reset, and `pwdn`
2. I2C probe and chip ID
3. mode table and format negotiation
4. host receiver and interrupt activity
5. userspace queueing and frame consumption
6. performance tuning

Do not start with epoll or lock optimization until the first five layers are stable.
