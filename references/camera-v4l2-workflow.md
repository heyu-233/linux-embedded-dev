# Camera V4L2 Workflow

Use this note for camera bring-up, V4L2, and media-controller debugging on Linux embedded boards.

## Minimum context

- board / SoC / kernel tree
- sensor model and bus: I2C, SPI, CSI, parallel
- host side block: CSI, ISP, bridge, codec
- DTS snippets for sensor, endpoint, clocks, reset, regulators
- symptom: probe fail, no `/dev/video*`, no frames, bad colors, timeout, low FPS

## Investigation order

1. Confirm hardware and DTS ownership
   - sensor node exists and matches the driver `compatible`
   - clocks, GPIOs, regulators, and endpoints are declared
   - endpoint graph is connected when the platform uses media controller
2. Confirm probe path
   - driver loads
   - I2C device responds if applicable
   - probe logs show resource acquisition and chip ID steps
3. Confirm video registration
   - `/dev/video*` exists
   - `v4l2-ctl --all` returns sane information
   - `media-ctl -p` shows the expected graph when applicable
4. Confirm capture path
   - format and resolution are supported
   - one known-good capture command works
   - frame timing, buffer allocation, and DMA path are stable
5. Confirm quality and performance
   - expected colorspace and Bayer order
   - dropped frames or timeout patterns
   - CPU and memory pressure during capture

## High-value commands

```bash
uname -a
dmesg | tail -n 200
v4l2-ctl --list-devices
v4l2-ctl --all -d /dev/video0
v4l2-ctl --list-formats-ext -d /dev/video0
media-ctl -p
i2cdetect -y 0
```

Adjust bus numbers and device nodes to the board.

## Common failure buckets

- **No device match**: DTS `compatible`, Kconfig, missing module, wrong bus
- **Probe resource failure**: clock, regulator, GPIO, reset timing, endpoint graph
- **Chip ID failure**: bus address, power-up sequence, clock, reset, register access
- **No `/dev/video*`**: host driver registration path failed or media graph incomplete
- **Stream failure**: format mismatch, lane config, DMA or buffer issue, unsupported mode
- **Bad image quality**: Bayer order, colorspace, stride, crop, sensor mode mismatch

## What to preserve in project notes

When a camera issue is solved, save:

- DTS node used
- owning driver files
- exact good capture command
- logs before and after the fix
- root cause and the minimal validation step
