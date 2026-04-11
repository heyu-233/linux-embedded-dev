# Device Tree And Driver Workflow

## Goal

Use this reference when the user is reading DTS or driver code, or when a device exists physically but Linux integration is incomplete.

## Read Order

1. DTS or DTSI node
2. binding expectations if available
3. driver `probe`
4. resource acquisition
5. registration path
6. userspace-visible result

## Ownership Questions

For each device, ask:

- who provides the clock?
- who enables regulators?
- who toggles reset or powerdown?
- who owns interrupts?
- who allocates memory or DMA buffers?
- who exposes the userspace interface?

## Review Risks

- device tree property name does not match driver expectation
- reset polarity mismatch
- clock enabled too late
- cleanup missing on probe failure
- node registers successfully but remains unusable in userspace
