# Char Device And Platform Driver Path

## Goal

Use this reference when the user wants a learning path for Linux embedded driver development, especially platform drivers and character-device style interfaces.

## Study Order

1. Device tree node or platform device registration
2. Driver match table and `probe`
3. Resource acquisition
   - memory region
   - IRQ
   - clocks
   - regulators
   - reset
4. Internal state structure
5. Registration of the userspace-facing interface
   - char device
   - misc device
   - subsystem-specific registration
6. File operations or ioctl path
7. Cleanup path
   - error unwind
   - remove
   - PM suspend or resume if relevant

## What To Learn First

- how matching happens
- what `probe` is allowed to assume
- how resources are acquired and released
- where the `/dev` node comes from
- who owns buffer memory and concurrency

## Review Checklist

- does `probe` handle partial failure cleanly?
- does remove or cleanup mirror allocation order?
- are locks protecting real shared state rather than accidental complexity?
- is the userspace API shape clear and minimally surprising?
- are lifetime and ownership rules documented in code flow?

## Good Teaching Pattern

When teaching this path, move from:

- DT node
- `probe`
- registration
- `/dev` visibility
- simple userspace open or ioctl
- error path and cleanup

That sequence keeps learning grounded in a full end-to-end path.
