# Project Learning Note

## Goal

Use this reference when the user wants durable local notes inside the current project, or when a milestone, bug fix, or performance investigation should be saved for later review.

## Default Policy

- Keep exactly one note file per project by default.
- The default path is `./linux-camera-learning-notes.md` in the current project root.
- If the file already exists, update that file rather than creating a new one.
- Only create multiple note files when the user explicitly asks for that structure.

## When To Update The Note

Update the project note when one of these happens:

- a major milestone is completed, such as bringing up the full camera pipeline
- a difficult bug is understood or fixed
- an optimization experiment reaches a meaningful conclusion
- a source-reading phase finishes with reusable understanding
- the user explicitly says to save, record, summarize, or log the result

Do not update the note after every tiny step unless the user asks for exhaustive journaling.

## What To Record

Each note entry should be compact and reusable. Prefer these fields:

- date
- title of the milestone, issue, or experiment
- project context, such as board, kernel branch, driver path, or application path
- what was attempted
- what was observed
- what finally worked or what remains unresolved
- important commands, logs, metrics, or code locations
- next actions

## Recommended File Shape

Use one Markdown file with a stable top-level structure, for example:

```md
# Linux Camera Learning Notes

## Project Snapshot
- board
- kernel or BSP branch
- sensor
- current capture path

## Milestones
### 2026-04-10 - Camera framework end-to-end running
- summary
- evidence
- remaining risks

## Hard Problems
### 2026-04-11 - First frame timeout root cause
- symptom
- root cause
- fix
- validation

## Optimization Log
### 2026-04-12 - Compared blocking DQBUF vs epoll LT
- baseline
- change
- result
- next step
```

The exact headings can be adjusted, but keep the file single and cumulative.

When initializing a fresh note or cleaning up an ad-hoc one, add a small reusable template under `Hard Problems` and `Optimization Log`. This keeps future updates consistent and lowers the friction of recording results during multi-day debugging or tuning.

Recommended template fields:

- `Hard Problems`
  - problem title
  - date
  - symptom
  - root cause
  - fix or current workaround
  - validation
  - remaining questions
- `Optimization Log`
  - experiment title
  - date
  - baseline
  - change
  - result
  - risk or side effect
  - next step

## Writing Style

- Write in Chinese by default, but keep technical identifiers, driver names, ioctl names, and commands in English.
- Keep entries short enough to scan later.
- Prefer evidence over narrative.
- If a conclusion is uncertain, label it as a hypothesis.

## Windows Encoding Guardrail

- When writing Chinese notes on Windows, do not send the Chinese body through a PowerShell inline here-string before another tool writes the file.
- Prefer direct file editing such as `apply_patch` for note updates.
- After writing, immediately read the note back and verify a few expected Chinese markers are intact. `UTF-8 with BOM` is useful, but it does not repair text that already became `?` before the file write.

## Interaction Pattern

When the user is actively debugging or tuning:

- do the work interactively in short phases
- wait for feedback between phases when appropriate
- once a meaningful checkpoint is reached, ask whether to update the project note if it is not already clearly requested
- if the user has previously indicated they want automatic recording, update the note at major checkpoints without creating extra files
