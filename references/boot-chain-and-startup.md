# Boot Chain And Startup

## Goal

Use this reference when the user is learning or debugging the Linux embedded startup path from power-on to userspace.

## Read Order

1. Boot ROM or SoC boot source rules
2. Bootloader stages
   - SPL or TPL when present
   - U-Boot or vendor loader
3. Kernel image and DTB loading
4. Boot arguments and memory layout
5. Kernel early boot
6. Driver init and probe order
7. Root filesystem mount
8. `init` and service startup

## Questions To Answer

- which component first fails?
- which image or DTB is actually being loaded?
- are bootargs the ones you think they are?
- does the kernel fail before rootfs, during rootfs, or after `init`?
- is the issue a boot problem or really a later probe or userspace problem?

## High-Value Evidence

- bootloader console log
- kernel early boot log
- final bootargs
- DTB filename and load address
- rootfs type and mount path
- first failing service or missing node

## Typical Failure Categories

- wrong DTB or stale image loaded
- rootfs mount failure
- console mismatch hiding useful logs
- early driver failure mistaken for boot failure
- userspace startup order issue after a healthy kernel boot
