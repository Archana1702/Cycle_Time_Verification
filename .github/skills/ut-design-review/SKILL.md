---
name: ut-design-review
description: 'Review a unit test design (UTD) for completeness, correctness, traceability, testability, and consistency with software requirements and design. Use for UT design reviews, test coverage audits, boundary/negative-case reviews, and identifying test specification gaps.'
argument-hint: 'Name the unit test design to review and any applicable requirements or software design documents.'
user-invocable: true
---

# Unit Test Design Review

## Purpose

Perform a findings-first review of a unit test design (UTD). Determine whether the proposed tests are correct, complete, traceable, deterministic, and implementable against the stated requirements and software design. A review identifies issues; do not edit the reviewed artifacts unless the user explicitly asks for remediation.

## Project Sources

For the VehicleStatus cycle-time SQT, review against:

- Requirements: `docs/SQT_REQUIREMENTS_PDU_Cycle_Time.md`
- Software design description: `docs/SWDD_PDU_Cycle_Time.md`
- Unit test design: `docs/UTD_PDU_Cycle_Time.md`
- Executable test inventory, when present: `docs/unit-test-design.csv`
- Implementation and tests, when present: `src/` and `tests/`

The SQT requirements are authoritative for externally observable behavior. The SWDD defines component responsibilities and design assumptions. Treat the UTD as the artifact under review, not as authority to redefine either source. Clearly distinguish a requirements defect from a design-derived robustness expectation or an implementation mismatch.

## Review Procedure

1. **Establish the review baseline.** Read the UTD and relevant requirement/design sources. Inspect implementation or test code only when the review asks about executable coverage or when needed to establish whether a test case is implementable. Record any unavailable source or unresolved conflict.
2. **Build a requirement-to-test map.** For every `REQ-*`, identify one or more UTD cases and the asserted behavior. Flag missing coverage, weak assertions, or traceability that points to a test which does not actually verify the requirement.
3. **Check expected behavior and test oracles.** Verify that each input can produce its stated expected result and that assertions discriminate PASS from FAIL. Check that failure cases assert useful failure evidence, not merely an overall FAIL.
4. **Check case completeness.** For this SQT, verify coverage of:
   - VehicleStatus identity and expected CAN ID `0x180`, including a correctly modeled wrong-ID candidate.
   - At least 10 valid samples and the insufficient 8-sample case.
   - Timestamp differences between consecutive valid samples; 10 samples yield 9 intervals.
   - Every measured interval and inclusive limits 90-110 ms.
   - Boundary outcomes: 90, 100, and 110 ms pass; 89 and 111 ms fail.
   - Specified negative examples: 85 ms and 115 ms fail.
   - Overall PASS only when every applicable check succeeds, and FAIL for each applicable violation.
   - Applicable failure diagnostics: index, timestamp, observed/expected ID, measured/allowed interval, sample counts, and reason.
5. **Check identity and data-model assumptions.** A wrong-ID frame can only be identified as a VehicleStatus candidate if PDU identity is supplied independently of its observed ID, such as fixture metadata or a configured mapping. Do not accept an arbitrary unrelated frame as proof of wrong-ID VehicleStatus traffic.
6. **Check unit-level quality.** Prefer isolated, deterministic, offline inputs; explicit preconditions; unambiguous expected results; no wall-clock delays or hardware dependencies; and tests that assert observable behavior rather than private implementation details. Confirm adapter, evaluator, diagnostic, and report tests target the appropriate component boundary.
7. **Check consistency and maintainability.** Look for duplicate cases without distinct value, gaps between test names and descriptions, ambiguous units, missing setup data, impossible sample/interval counts, and cases that combine unrelated behaviors so failures are hard to diagnose.
8. **Report findings before summary.** Order actionable findings by severity and cite the exact UTD section, case ID, or test name. Use severity labels consistently:
   - **High:** requirement not tested, incorrect expected result, or a false-pass path.
   - **Medium:** important diagnostic, boundary, negative, or component-isolation gap that weakens confidence.
   - **Low:** clarity, traceability, redundancy, or maintainability issue with limited behavioral impact.
   Do not report preferences as defects. If there are no findings, say so and identify any remaining coverage gaps or review limitations.

## VehicleStatus Review Invariants

- PDU name: `VehicleStatus`.
- Expected CAN ID: `0x180`.
- Minimum valid samples: 10.
- Interval count at 10 valid samples: 9.
- Valid interval: inclusive `[90 ms, 110 ms]`.
- 90 ms and 110 ms are passing boundaries; 89 ms and 111 ms fail.
- 85 ms and 115 ms negative examples fail.
- A failure in any applicable check prevents overall PASS.
- Wrong-ID scenarios require PDU candidate identity independent of the observed ID.

## Output Format

Use this concise structure:

```text
Findings
- [High|Medium|Low] <issue and consequence> — <UTD section, case ID, or test name>

Coverage
- REQ-...: covered / partial / missing — <case IDs and reason>

Assumptions and limitations
- <unresolved conflict, unavailable artifact, or none>

Summary
- <overall review conclusion and most important remaining gap>
```

If there are no findings, state “No findings” first. Do not claim tests were executed during a design-only review. If executable coverage is also reviewed, name the command and report its actual outcome separately.