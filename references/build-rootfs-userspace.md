# Build Rootfs Userspace

## Goal

Use this reference for topics above the kernel line: root filesystem, init flow, services, package integration, and application bringup.

## Focus Areas

- build system choice and layout
  - Buildroot
  - Yocto
  - vendor BSP rootfs
- init path
  - bootargs
  - `init`
  - service manager
- device access
  - `/dev`
  - permissions
  - udev or mdev behavior
- application startup
  - config files
  - dependencies
  - launch ordering

## Common Questions

- why does probe succeed but userspace still fail?
- why is the node missing after boot?
- why does the app work manually but fail as a service?
