# OSS Inspired Flows

## labgrid Style

```text
target -> resource -> driver -> action -> evidence
```

Use this style when the board has multiple controllable resources and we need explicit ownership boundaries.

## tbot Style

```text
host -> bootloader -> Linux shell -> task -> result
```

Use this style when the main value is repeatable board sessions with readable steps.

## pytest-embedded Style

```text
flash -> reset -> serial assertion -> result classification
```

Use this style for MCU targets where the serial log is the main truth source.

## AutoEmbed Style

```text
generate -> build -> deploy -> verify -> record
```

Use this style when the loop is explicitly closed and each stage leaves a durable artifact.
