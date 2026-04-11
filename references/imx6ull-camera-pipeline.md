# i.MX6ULL Camera Pipeline

## Overview

For your study path, think in one concrete chain:

`OV5640 -> board power and GPIO sequencing -> sensor driver -> CSI or capture host -> V4L2 video node -> mmap buffers -> userspace DQBUF or QBUF loop`

The exact block names differ across BSP and upstream trees, but the debugging questions stay similar: did the sensor start correctly, did the host receive frames, did buffers complete, and did userspace return buffers fast enough?

## Step 1: Board-Level Preconditions

Before any V4L2 discussion, confirm the board-level facts:

- Sensor input clock is present and at the expected frequency.
- `reset` and `pwdn` GPIO polarity matches the board wiring.
- I2C address and bus number are correct.
- Power rails and sequencing are stable before probe and stream-on.
- Parallel bus or endpoint wiring matches the DTS description used by the kernel.

If these are wrong, userspace optimization is irrelevant because the pipeline is already broken before streaming.

## Step 2: Sensor Driver Perspective

At the sensor-driver level, `ov5640` is responsible for:

- chip ID detection over I2C
- power-on and power-off sequencing
- reset and standby control
- pixel format and frame size negotiation
- frame interval related settings
- V4L2 controls such as exposure or gain, depending on branch support

Typical questions:

- Did probe succeed and read the expected chip ID?
- Is stream-on actually programming the sensor registers for the selected mode?
- Is the output format the same one the host driver expects?

## Step 3: Capture Host Perspective

On i.MX6ULL BSP-style trees, the capture host and CSI path may use naming that looks different from upstream documentation. Treat the host side as the block that:

- receives pixel data from the sensor-facing interface
- configures bus format and frame geometry
- programs DMA or buffer descriptors
- marks a buffer done when a frame lands
- wakes the waiting userspace thread or poller

This is the layer to inspect when:

- the sensor seems alive but no frame reaches `/dev/videoX`
- frame interrupts occur but buffers are not completed correctly
- CPU usage is high because the wakeup path or queue flow is inefficient

## Step 4: V4L2 Video Node Perspective

The V4L2 node is where userspace sees the stream. The useful mental model is:

- `open()` establishes the file handle
- `VIDIOC_S_FMT` and related ioctls negotiate the video format
- `VIDIOC_REQBUFS` allocates a streaming queue
- `VIDIOC_QUERYBUF` exposes offsets for `mmap`
- `VIDIOC_QBUF` hands empty buffers to the driver
- `VIDIOC_STREAMON` starts streaming
- `VIDIOC_DQBUF` returns a filled buffer
- userspace processes the frame and calls `VIDIOC_QBUF` again

If any of these state transitions are delayed or broken, CPU and frame-rate behavior will suffer even when the sensor and host are otherwise correct.

## BSP vs Upstream Terminology

Use this translation pattern when reading code and answering questions:

- BSP tree names may emphasize platform blocks and legacy capture flow.
- Upstream media docs often emphasize subdevs, media graph links, bus formats, and standard V4L2 queue semantics.
- When explaining to the user, map both onto the same path: sensor -> host -> buffer queue -> userspace.

That translation matters because many optimization ideas make sense only when you know which layer owns the cost.

## Where CPU Usually Goes

In a working pipeline, CPU overhead usually comes from a small set of places:

- too many wakeups per frame or unnecessary polling
- slow frame processing before requeue
- extra memory copies or format conversion
- lock contention in queue or completion paths
- DMA or cache maintenance cost
- logging, tracing, or debugging left enabled on the hot path

A sensor or CSI throughput limit can also cap frame rate without high CPU. Do not confuse throughput ceilings with software overhead.

## Source-Reading Order For i.MX6ULL

When the kernel tree is available, read in this order:

1. board DTS or camera-related DTS includes
2. `ov5640` driver
3. capture host or CSI driver used by the branch
4. userspace test app or capture application

That order keeps the physical wiring, sensor state, host buffering, and application loop connected in one mental model.
