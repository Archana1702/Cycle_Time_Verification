---
name: pdu-cycle-time-sqt
description: 'Use for the VehicleStatus CAN PDU software qualification workflow: analyze SQT requirements, create or update the SWDD and unit test design, implement pytest automation, execute/debug tests, and maintain requirement traceability through CI.'
argument-hint: 'Name the workflow stage or artifact and the requested outcome, such as SWDD, unit test design, pytest implementation, debugging, or CI.'
user-invocable: true
---

# PDU Cycle-Time SQT Workflow

## Purpose

Guide requirement-driven software qualification work for the VehicleStatus CAN PDU. Use this workflow for a single requested stage or for a sequence of stages; do not create every artifact when the user requests only one.

## Project Sources

- SQT requirements: `docs/SQT_REQUIREMENTS_PDU_Cycle_Time.md`
- Software design description: `docs/SWDD_PDU_Cycle_Time.md`
- Unit test design: `docs/UTD_PDU_Cycle_Time.md`
- Project conventions: `.github/copilot_instructions.md`

Read the applicable existing sources and nearby implementation/tests before editing. The SQT requirements define externally observable acceptance behavior and take precedence if a design document conflicts. The SWDD defines intended component responsibilities and assumptions. The unit test design elaborates test cases but cannot weaken requirements. State unresolved contradictions or missing inputs rather than silently inventing behavior.

## Workflow

1. **Identify the requested stage.** Determine whether the task is requirements analysis, software design, unit test design, pytest automation, test execution/debugging, refactoring/review, or CI. Find the closest owning document, implementation, test, or workflow file. Keep scope to the requested stage and its necessary dependencies.
2. **Establish traceability.** Map the work to relevant `REQ-PDU-*` identifiers. Preserve the SQT baseline: `VehicleStatus`, CAN ID `0x180`, at least 10 valid samples, intervals measured between consecutive valid samples, and inclusive limits of 90 ms through 110 ms. At 10 samples, there are 9 adjacent-sample intervals.
3. **Resolve input identity correctly.** A wrong-ID test requires a candidate identified as `VehicleStatus` independently of its observed CAN ID, for example via fixture metadata or configured mapping. Do not characterize an arbitrary `0x181` CAN frame as a wrong-ID VehicleStatus message without that association.
4. **Produce only the requested artifact.**
   - For a software design, describe scope, components, data flow, interfaces, result logic, diagnostics, verification, assumptions, and requirement traceability.
   - For a unit test design, specify deterministic fixtures, inputs, expected results, failure diagnostics, test IDs/names, and traceability. Separate requirement-mandated behavior from additional design-derived error handling.
   - For test automation, follow the design and existing Python 3.11+/pytest conventions. Prefer pure, deterministic unit tests and keep acquisition, evaluation, diagnostics, and reporting responsibilities separate.
   - For execution or debugging, run the narrowest relevant pytest command first, use its result to locate the owning defect, and rerun the same focused test after a fix.
   - For CI or review, verify the existing workflow and report concrete failures, missing coverage, or requirement gaps without broadening scope unnecessarily.
5. **Cover the required decision points.** Tests and designs should account for correct ID, wrong candidate ID (`0x181` example), at least 10 samples, insufficient samples (8 example), consecutive timestamp differences, all measured intervals, inclusive 90/110 ms boundaries, and failures at 89/111 ms. Also include 85/115 ms negative examples where relevant. PASS is permitted only when every applicable requirement passes; otherwise the result is FAIL.
6. **Check diagnostic quality.** For each failure, include applicable sample/source index, timestamp, observed and expected CAN IDs, measured cycle time, expected range, observed/required sample count, and a clear reason. Prefer assertions on structured fields over brittle full-message string comparisons.
7. **Validate after edits.** Run the narrowest available executable check, usually a focused `python -m pytest ...` command for Python changes. For documentation-only work, inspect rendered Markdown/link targets or use available diagnostics. Report commands and outcomes accurately; never state that tests passed unless they were run.
8. **Summarize completion.** State files changed, requirements covered, validation performed, and any assumptions or remaining gaps. Preserve unrelated user modifications and do not add ECU firmware, flashing, CANoe/HIL, production infrastructure/security, or AWS publishing unless explicitly requested as an optional training extension.

## Acceptance Checklist

- [ ] Requested stage and scope are clear; unrelated deliverables were not added.
- [ ] Applicable requirements are traceable to design decisions or tests.
- [ ] Timing comparisons are inclusive and performed without rounding before validation.
- [ ] Ten valid samples are distinguished from the nine intervals they produce.
- [ ] Wrong-ID scenarios preserve independent PDU candidate identity.
- [ ] PASS/FAIL and failure diagnostics match the SQT requirements.
- [ ] Relevant validation was executed or its absence is explicitly explained.