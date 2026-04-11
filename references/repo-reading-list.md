# Repo Reading List

## Purpose

Use this reading list when the user wants a compact, high-signal study path instead of randomly browsing Linux camera repositories. The order below is intentional: practical i.MX6 context first, then BSP kernel truth, then upstream contrast, then userspace tools and minimal examples.

## 1. Freescale/gstreamer-imx

- Repo: [Freescale/gstreamer-imx](https://github.com/Freescale/gstreamer-imx)
- Why read it first:
  - It captures a lot of real-world i.MX BSP pain points in one place.
  - It explains why old i.MX capture stacks often need platform-specific handling rather than naive generic V4L2 assumptions.
- Focus on:
  - README and plugin descriptions around `imxv4l2videosrc`, allocators, and zero-copy behavior.
  - Notes mentioning `mxc_v4l2` limitations or BSP-specific expectations.
- Questions it answers:
  - Why does i.MX6 capture sometimes behave differently from textbook V4L2 examples?
  - Where do zero-copy expectations and platform allocators start to matter?
  - Why can userspace design choices expose BSP driver limitations?

## 2. nxp-imx/linux-imx

- Repo: [nxp-imx/linux-imx](https://github.com/nxp-imx/linux-imx)
- Why read it second:
  - This is the most important source of truth for NXP BSP behavior.
  - Your actual i.MX6ULL camera path is usually easier to explain from BSP code than from upstream abstractions.
- Focus on:
  - Sensor driver paths such as `drivers/media/i2c/ov5640.c` in branches that contain the driver.
  - Capture-host or CSI-related drivers used by the BSP branch for i.MX6 family camera input.
  - DTS or board files that define sensor reset, powerdown, clocks, endpoints, and bus wiring.
- Questions it answers:
  - Which driver actually owns the queue and wakeup path on the BSP kernel?
  - How are OV5640 clocks, reset GPIOs, and pixel formats described in the BSP?
  - Which parts of the path are NXP-specific and not portable upstream?

## 3. torvalds/linux

- Repo: [torvalds/linux](https://github.com/torvalds/linux)
- Why read it third:
  - Upstream gives you cleaner subsystem intent and terminology.
  - It is the best contrast layer when BSP naming is confusing or outdated.
- Focus on:
  - `drivers/media/i2c/ov5640.c`
  - Media subsystem patterns around probe, power sequencing, controls, and format negotiation.
  - Documentation for i.MX media where available, such as the kernel docs for i.MX video capture.
- Questions it answers:
  - What is the upstream mental model for sensor state, controls, and media graph behavior?
  - Which BSP patterns are legacy shortcuts versus current subsystem expectations?
  - How should you translate BSP behavior into standard V4L2 and media-controller language?

## 4. gjasny/v4l-utils

- Repo: [gjasny/v4l-utils](https://github.com/gjasny/v4l-utils)
- Why read it fourth:
  - It contains the userspace tools you will use to inspect and validate the stack.
  - It helps you turn fuzzy driver questions into concrete observations.
- Focus on:
  - `v4l2-ctl`, `media-ctl`, and `qv4l2` related code and docs.
  - Option handling around format listing, streaming, control inspection, and media-topology display.
- Questions it answers:
  - How do you inspect the device, graph, controls, and negotiated format quickly?
  - Which command-line checks should be used before touching the application or driver?
  - How can you confirm whether the bottleneck is configuration, stream timing, or userspace behavior?

## 5. 6by9/yavta

- Repo: [6by9/yavta](https://github.com/6by9/yavta)
- Why read it fifth:
  - It is a compact reference for the V4L2 streaming state machine.
  - It avoids the abstraction noise common in larger camera applications.
- Focus on:
  - Buffer allocation and queueing code.
  - Streaming loop structure around `DQBUF` and `QBUF`.
  - Nonblocking and low-overhead testing patterns.
- Questions it answers:
  - What is the minimal correct streaming loop for V4L2 capture?
  - Where should requeue happen relative to frame processing?
  - What behavior is required by V4L2 itself rather than by your application framework?

## 6. libcamera/libcamera

- Repo: [libcamera/libcamera](https://github.com/libcamera-org/libcamera)
- Why read it last and selectively:
  - It is not your immediate implementation baseline for i.MX6ULL BSP work.
  - It is still useful for modern vocabulary and long-term architecture intuition.
- Focus on:
  - Request and buffer ownership concepts.
  - Pipeline handler design and asynchronous flow vocabulary.
- Questions it answers:
  - How do modern Linux camera stacks talk about requests, ownership, and scheduling?
  - Which ideas are worth borrowing mentally even if you stay on BSP V4L2 code?

## Suggested Reading Order By Goal

- If the goal is bringup or source reading:
  - `linux-imx` -> `torvalds/linux` -> `gstreamer-imx`
- If the goal is userspace capture-loop optimization:
  - `yavta` -> `v4l-utils` -> `gstreamer-imx`
- If the goal is architecture learning:
  - `gstreamer-imx` -> `linux-imx` -> `torvalds/linux` -> `libcamera`

## What To Extract Into Notes

For each repo, keep the notes short and practical:

- Which part of the pipeline it helps explain
- Which files or modules are worth reading first
- Which assumptions are BSP-only versus upstream-friendly
- Which measurements or commands it suggests before optimization
