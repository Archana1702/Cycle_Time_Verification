---
name: ut-test-design
description: 'Create or update requirement-traceable unit test designs for the VehicleStatus CAN PDU cycle-time qualification project. This skill produces test specifications only and does not implement code.'
argument-hint: 'Describe the requirement, behavior, or test-design artifact to create or update.'
user-invocable: true
---

# Unit Test Design

## Purpose

Turn software requirements and design decisions into clear, deterministic, traceable unit test cases. Use this skill when creating, updating, or checking a unit test design, not when implementing automated tests.

## Strict TDD Constraint

**Do not create, modify, or generate an actual code implementation.** This includes production code and executable test code such as Python or pytest files. TDD is followed by designing and documenting the tests first; code implementation is a separate, later task and must not be performed as part of this skill. Only edit requested test-design artifacts, such as Markdown documents or CSV test-case inventories.

## Sources of Truth

- Requirements: `docs/SQT_REQUIREMENTS_PDU_Cycle_Time.md`
- Software design: `docs/SWDD_PDU_Cycle_Time.md`
- Unit test design: `docs/UTD_PDU_Cycle_Time.md`
- Test-case inventory, when present: `docs/unit-test-design.csv`

Requirements govern externally observable behavior. Use the software design for component boundaries and design-derived behavior. If sources conflict or leave behavior undefined, record the conflict or assumption instead of inventing an expected result.

## Workflow

1. Identify the requested behavior and read only the relevant requirements, design sections, and existing test-design entries.
2. Map each proposed case to applicable `REQ-PDU-*` identifiers. Keep requirement-mandated behavior distinct from robustness cases derived from the software design.
3. Specify each case with a stable ID, descriptive test name, objective, preconditions, deterministic inputs, steps, expected result, and applicable diagnostic checks. Follow the existing UTD or CSV format.
4. Cover relevant nominal, negative, and boundary conditions. Ensure each expected result follows from its source requirement and each case can distinguish pass from fail.
5. Review the design for missing requirement coverage, ambiguous inputs, impossible sample/interval counts, duplicated cases, and traceability gaps. State assumptions and unresolved questions.
6. Edit only the requested test-design artifacts. Do not add or change implementation or executable test files.
7. Summarize the artifacts updated, requirement coverage, assumptions, and remaining design gaps. Do not claim tests were executed for a design-only task.

## VehicleStatus Design Invariants

- PDU: `VehicleStatus`; expected CAN ID: `0x180`.
- At least 10 valid samples are required; 10 samples yield 9 intervals.
- Measure each interval between consecutive valid sample timestamps.
- The accepted cycle-time range is inclusive: 90 ms through 110 ms.
- 90, 100, and 110 ms pass; 89 and 111 ms fail. Include 85 and 115 ms negative examples where relevant.
- Overall PASS requires every applicable check to pass; any applicable violation produces FAIL.
- Specify failure diagnostics where applicable, including sample index, timestamp, observed and expected IDs, measured and allowed cycle time, counts, and reason.
- A wrong-ID case must identify the candidate as `VehicleStatus` independently of its observed CAN ID. An unrelated frame alone is not a valid wrong-ID case.
- Keep test data deterministic and offline; do not require wall-clock delays, CAN hardware, network access, or external services.

## Output

Provide or update the requested test-design artifact(s), then report:

- Test-case IDs and requirements covered.
- Any assumptions, source conflicts, or unresolved gaps.
- The files changed.

Do not include executable implementation code in the design deliverable.