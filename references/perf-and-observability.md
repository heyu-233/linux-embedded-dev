# Perf And Observability

## Goal

Use this reference when the user wants to optimize CPU, latency, memory behavior, or throughput on a Linux embedded system.

## Principle

Measure first. Do not jump straight to structural changes.

## Useful Tools

- `top`
- `vmstat`
- `iostat`
- `strace`
- `perf`
- `ftrace`
- subsystem-specific tools such as `v4l2-ctl` or `i2cdetect` when appropriate

## Questions To Answer

- is the system CPU-bound or waiting?
- is wakeup frequency excessive?
- is copy cost dominating?
- is the hot path in userspace or kernel?
- is the bottleneck functional, architectural, or simply a configuration limit?

## Output Shape

When suggesting an optimization, record:

- baseline
- change
- result
- side effect
- next step
