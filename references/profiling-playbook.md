# Profiling Playbook

## Goal

Use these commands to decide where time is going before changing the architecture. The exact commands may vary by BSP image, but the questions remain stable.

## 1. Confirm Device and Format State

```bash
v4l2-ctl -D -d /dev/video0
v4l2-ctl -d /dev/video0 --all
v4l2-ctl -d /dev/video0 --list-formats-ext
```

Use this to confirm:

- active driver and card name
- negotiated format and dimensions
- control state
- whether the device exposed what you think it exposed

## 2. Inspect Media Topology

```bash
media-ctl -p
```

Use this when the platform exposes media-controller topology. It helps confirm sensor-to-host links, enabled pads, and endpoint assumptions.

## 3. Run a Minimal Streaming Test

```bash
v4l2-ctl -d /dev/video0 --stream-mmap=4 --stream-count=200 --stream-to=/dev/null
```

Or, when available:

```bash
yavta -c200 -n4 -f UYVY -s 640x480 /dev/video0
```

Use this to separate driver and queue behavior from your full application.

## 4. Check Process-Level CPU

```bash
top -H -p <pid>
vmstat 1
```

Questions to answer:

- Which thread is hot?
- Is the system CPU-bound, context-switch heavy, or mostly idle?
- Does CPU spike line up with frame handling or with something else?

## 5. Check Syscall Shape

```bash
strace -tt -T -p <pid>
```

Useful observations:

- repeated short waits can point to excessive wakeups
- large time inside `ioctl` can indicate blocking wait or driver-side stall
- unexpected `poll`, `select`, or `read` loops can reveal framework behavior you forgot about

## 6. Sample Hotspots With perf

```bash
perf top
perf record -g -p <pid> -- sleep 10
perf report
```

Use this to identify:

- memcpy or format conversion hotspots
- lock contention or scheduler overhead
- driver functions that dominate time on CPU

## 7. Trace Timing With ftrace

Exact tracepoints vary by kernel, but useful directions include:

- scheduler latency
- IRQ handler timing
- wakeup timing
- function graph tracing around camera or queue functions

Typical workflow:

- trace a short capture window
- look for long gaps between frame completion and userspace wakeup
- compare queue activity before and after an optimization

## How To Interpret Results

- If minimal `v4l2-ctl` or `yavta` streaming is already expensive, inspect driver path before touching app design.
- If the minimal test is cheap but the full app is expensive, inspect copy, conversion, and event-loop complexity in userspace.
- If both are cheap but frame rate is low, inspect sensor mode, bus format, and throughput ceilings.
- If only long runs degrade, inspect leaks, buffer starvation, logging, or thermal or scheduler effects.

## Output To Save In Notes

For each profiling session, keep:

- kernel version or BSP release
- device format and frame size
- buffer count
- frame rate and drop count
- top two CPU hotspots
- whether the queue ever starved
- what changed between runs
