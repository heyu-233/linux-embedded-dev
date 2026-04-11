# Linux Embedded Debug Workflow

## Goal

Use this reference when the user has a real bug and needs a disciplined debug path.

## Workflow

1. Define the failure boundary.
   - boot failure
   - probe failure
   - missing device node
   - userspace open failure
   - bad data path
   - performance regression
2. Collect first evidence.
   - boot log
   - `dmesg`
   - relevant `/sys` or `/proc` state
   - device nodes
   - module list
   - config fragments
3. Map dependencies.
   - clock
   - power
   - reset
   - bus reachability
   - firmware or DT binding
4. Test with the smallest useful command.
   - prefer short, phase-based steps
   - wait for output before expanding the procedure
5. Convert findings into a durable note.
   - symptom
   - root cause
   - fix
   - validation

## Typical Failure Categories

- probe path misconfigured
- device tree mismatch
- resource ownership mismatch
- userspace expecting the wrong node or API
- performance issue misdiagnosed as functional failure
