---
name: PDU Cycle-Time SQT Task
description: Create or update one SQT artifact using the PDU cycle-time requirements and software design description.
argument-hint: Describe the single artifact or workflow stage to work on, such as test design, pytest automation, execution/debugging, or CI validation.
agent: agent
---

Work on this requested task: ${input:task}

Use these project documents as the source of truth:

- Requirements: [SQT_REQUIREMENTS_PDU_Cycle_Time.md](../../docs/SQT_REQUIREMENTS_PDU_Cycle_Time.md)
- Software design: [SWDD_PDU_Cycle_Time.md](../../docs/SWDD_PDU_Cycle_Time.md)

Before making changes, read both documents and inspect the closest existing code, tests, or documentation relevant to the requested task. Treat the requirements as authoritative for externally observable behavior and the SWDD as the intended software structure. If they conflict, do not silently choose one: explain the conflict and keep changes consistent with the requirements unless the user directs otherwise.

Project context:

- This is a Python 3.11+ software qualification testing training project. Use pytest and existing repository conventions.
- The subject is the `VehicleStatus` PDU, expected CAN ID `0x180`.
- A valid sample has the expected PDU identity and CAN ID. Require at least 10 valid samples; 10 samples yield 9 adjacent-sample cycle intervals.
- Calculate intervals from consecutive valid sample timestamps using a common, sufficiently precise time unit. Compare without rounding against the inclusive range 90 ms to 110 ms.
- PASS only when every applicable identification, presence, sample-count, and cycle-time check succeeds. Report actionable diagnostics on failure, including relevant sample/source index, timestamp, observed and expected CAN IDs, measured and allowed cycle times, and failure reason.
- Cover wrong CAN ID, 85 ms and 115 ms intervals, 8 samples, and the timing boundaries: 90 ms and 110 ms pass; 89 ms and 111 ms fail.
- Wrong-ID detection requires an input source or fixture that identifies the candidate PDU independently of its observed CAN ID. Do not claim an arbitrary CAN frame is a wrong-ID `VehicleStatus` message without that mapping.
- Keep acquisition, qualification logic, diagnostics, and reporting separated as described in the SWDD. Prefer deterministic offline fixtures; hardware access is not required for the MVP.
- Do not add ECU firmware, flashing, hardware-in-the-loop, production infrastructure/security, or AWS publishing unless the requested task explicitly concerns an optional training extension.

Implementation expectations:

1. Keep the change limited to the requested artifact or workflow stage. Preserve unrelated user changes.
2. Maintain traceability to the applicable `REQ-PDU-*` requirement IDs in tests or documentation where useful.
3. Add or update focused tests for behavior changes, including relevant negative and boundary cases.
4. Run the narrowest relevant pytest, type, lint, or documentation validation available after editing. Report the command and outcome; state clearly if validation could not be run.
5. Summarize files changed, requirement coverage, and any assumptions or unresolved conflicts. Do not claim tests passed unless they were executed.