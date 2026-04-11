# Common Bus Debugging

## Goal

Use this reference when the user is debugging peripheral communication on common Linux embedded buses such as I2C, SPI, UART, or MMC.

## Shared Workflow

1. Confirm physical prerequisites.
   - power
   - clock
   - reset
   - pinmux
   - pull-up or pull-down requirements
2. Confirm device tree wiring.
   - bus node enabled
   - child node address or chip select
   - interrupt and reset GPIOs
   - compatible string
3. Confirm probe evidence.
   - boot log
   - `dmesg`
   - sysfs or `/dev` visibility
4. Run the smallest useful bus-specific command.
5. Separate link failure from higher-level protocol failure.

## I2C

- check bus number and address
- verify pull-ups and clock
- confirm `i2cdetect` and driver probe match expectations
- distinguish no-ack from wrong register behavior

## SPI

- check chip select mapping
- verify mode, polarity, and phase
- confirm max frequency is realistic
- separate transfer framing bugs from probe issues

## UART

- check baud, parity, and flow control
- verify pinmux and console ownership
- distinguish line-noise problems from wrong tty selection

## MMC or SD

- check bus width and voltage
- verify card-detect behavior
- inspect timing mode assumptions
- distinguish enumeration failure from filesystem failure

## Review Risks

- wrong bus instance
- stale DTS copied from another board
- probe succeeds but communication is still broken
- userspace test tool masks the real transport issue
