# V4L2 Buffer Lifecycle

## Overview

The core V4L2 streaming path is not complicated, but many camera performance bugs come from misunderstanding buffer ownership and queue timing rather than from exotic kernel problems.

## The Canonical Streaming Sequence

A minimal `mmap` capture loop looks like this:

1. `open()` the device
2. negotiate format with `VIDIOC_S_FMT` or inspect with `VIDIOC_G_FMT`
3. allocate buffers with `VIDIOC_REQBUFS`
4. inspect each buffer with `VIDIOC_QUERYBUF`
5. `mmap()` the buffers
6. queue all available buffers with `VIDIOC_QBUF`
7. start streaming with `VIDIOC_STREAMON`
8. repeat:
   - wait for data readiness
   - `VIDIOC_DQBUF`
   - process frame quickly
   - `VIDIOC_QBUF` to return the buffer
9. stop with `VIDIOC_STREAMOFF`

## Buffer Ownership Mental Model

Use these states when reviewing code:

- free in userspace: mapped but not currently handed to the driver
- queued in driver: available for capture hardware
- filled by hardware: capture completed, waiting to be dequeued
- dequeued in userspace: application owns it until requeue

Only one side owns the buffer at a time. Most bugs are really ownership bugs.

## What Blocking DQBUF Means

With a blocking file descriptor, `VIDIOC_DQBUF` sleeps until a filled buffer is available or an error occurs. For a single stream, this is often perfectly acceptable and can be the simplest low-CPU design.

Use blocking `DQBUF` when:

- there is a single capture source
- the frame processing path is straightforward
- you do not need a unified event loop for multiple FDs
- you want the simplest correctness story

## What poll or epoll Adds

`poll()` or `epoll()` adds value when you need to wait on multiple file descriptors or combine camera readiness with control sockets, IPC, timers, or shutdown events.

Level-triggered waiting is usually easier because readiness remains visible until you consume it correctly.

## Why epoll ET Is Not A Default Win

`epoll` edge-triggered can reduce redundant wakeups in some designs, but it is not automatically better for camera capture.

Common risks:

- missing a readiness edge because the loop does not drain correctly
- more complex state handling with little CPU benefit on a single stream
- masking the real bottleneck, which is often copy, conversion, or queue turnaround

Treat `epoll ET` as a design experiment only after measurement shows wakeup overhead matters.

## Where CPU Time Is Commonly Spent

- userspace image processing before requeue
- extra copy from `mmap` buffer into another staging buffer
- colorspace or format conversion on every frame
- busy loops around readiness checks
- excessive logging on every frame
- slow buffer return that starves the queue

## Review Questions For Any Capture Loop

- Are all buffers queued before `STREAMON`?
- Is every successful `DQBUF` eventually followed by `QBUF`?
- Can frame processing block so long that the queue depth becomes too small?
- Does timeout or error handling accidentally leak a buffer out of circulation?
- Is nonblocking mode paired with correct `EAGAIN` handling?
- If `epoll ET` is used, does the code reliably consume all ready state before sleeping again?

## Simple Decision Rule

- Start with blocking `DQBUF` if the app is single-purpose and simple.
- Use `poll` or `epoll` level-triggered when integrating multiple FDs.
- Consider `epoll ET` only when profiling shows readiness wakeups are a material overhead and the code can safely manage the added complexity.
