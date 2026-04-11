# Review Checklist

## Goal

Use this checklist when reviewing Linux camera code, especially V4L2 capture loops, BSP camera drivers, and queue or wakeup path changes.

## Userspace Capture Loop

Check for:

- all buffers queued before `STREAMON`
- every successful `DQBUF` followed by a reachable `QBUF`
- error paths that do not silently leak a buffer
- bounded processing time before requeue
- correct handling of `EAGAIN`, timeout, and shutdown conditions
- event-loop logic that cannot miss readiness or sleep forever

## Driver Queue and Wakeup Path

Check for:

- clear ownership transitions between hardware, driver, and userspace
- wakeup only after buffer state is truly visible and stable
- no missed completion because of list corruption or wrong state ordering
- queue depth preserved across transient errors where possible
- no long critical section around operations that can move out of the lock

## Locking

Check for:

- spinlock or mutex held while doing avoidable work
- lock order that can deadlock under stream-on, stream-off, or interrupt timing
- IRQ-sensitive data touched without clear protection
- retries or busy loops caused by unclear queue state

## Format and Throughput

Check for:

- unnecessary copy or conversion in the hot path
- buffer size or count too small for the chosen mode
- frame interval and format assumptions not validated against device capability
- throughput regressions hidden behind average frame-rate numbers

## Regression Risks To Call Out

- lower CPU but worse latency or more drops
- fewer wakeups but missed frame readiness under load
- narrower lock scope but broken ordering or visibility
- faster short benchmark but unstable long-run capture

## Review Output Shape

When writing findings, prefer:

- the exact bottleneck or correctness risk
- the evidence path, such as code location or measurement
- the likely impact on frame rate, CPU, latency, or stability
- the safest next validation step
