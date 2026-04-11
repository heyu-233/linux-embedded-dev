# Performance Tuning Checklist

## Principle

Optimize from evidence, not from folklore. In camera capture paths, the biggest wins often come from queue depth, copy reduction, and better frame turnaround rather than from changing the event API.

## Tuning Order

1. Measure the baseline.
   - frame rate
   - drop rate
   - end-to-end latency if relevant
   - per-process CPU usage
   - syscall and wakeup behavior
2. Check queue health.
   - number of V4L2 buffers
   - how long a buffer stays in userspace before requeue
   - whether the queue is occasionally starved
3. Check copy and conversion cost.
   - extra memcpy
   - YUV or RGB conversion
   - scaling or compression in the hot path
4. Check readiness and wakeups.
   - blocking `DQBUF`
   - `poll` or `epoll`
   - timer wakeups, busy waits, or spin loops
5. Check locking and synchronization.
   - long critical sections
   - locks taken in IRQ-sensitive paths
   - queue ownership confusion causing retries or stalls
6. Check DMA, cache, and memory behavior.
   - cache maintenance cost
   - allocator choice
   - physically contiguous memory constraints on BSP stacks
7. Check scheduler and system effects.
   - CPU affinity
   - competing threads
   - noisy logs or tracing left enabled

## Decision Table

| Design | When to prefer it | Main upside | Main risk |
| --- | --- | --- | --- |
| blocking `DQBUF` | single camera, simple loop, minimal coordination | simplest correctness and often low CPU | hard to integrate with extra FDs |
| `poll` or `epoll` level-triggered | multiple FDs, shutdown events, IPC, control channels | flexible and usually easy to reason about | more loop structure than blocking wait |
| `epoll` edge-triggered | measured wakeup overhead matters and loop can drain readiness correctly | can reduce redundant wakeups in some designs | missed events, more state bugs, often small real gain |

## What Usually Matters More Than epoll ET

- insufficient buffer count
- slow frame processing before `QBUF`
- unnecessary memcpy or format conversion
- keeping a lock while doing too much work
- queue starvation after transient errors
- userspace and driver disagreeing about when a buffer is reusable

## Spinlock Guidance

Do not optimize spinlocks by instinct. First answer these questions:

- Is the lock actually hot in `perf` or `ftrace`?
- Is the critical section larger than it needs to be?
- Is work inside the lock doing format conversion, list walking, or memory management that could move out?
- Is a lock being used to compensate for unclear ownership rather than true shared-state needs?

Reducing lock hold time is usually safer than replacing a lock primitive.

## Safe Optimization Pattern

- change one bottleneck at a time
- keep a before and after metric table
- validate frame rate, CPU, and stability together
- long-run test after each structural change

## Example Bottleneck Interpretations

- High CPU with normal frame rate and many syscalls: wakeup or polling design may matter.
- High CPU with heavy memcpy: prioritize copy reduction before event-loop changes.
- Low CPU but bad frame rate: check sensor mode, bus bandwidth, queue starvation, or host throughput ceiling.
- Good average frame rate but jitter or drops: check long userspace processing gaps, missed requeue, or lock contention spikes.
