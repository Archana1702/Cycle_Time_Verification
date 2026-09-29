# Unit Test Design: PDU Cycle-Time Qualification

## 1. Purpose

This document defines unit-level verification for the software qualification test described in [SQT_REQUIREMENTS_PDU_Cycle_Time.md](SQT_REQUIREMENTS_PDU_Cycle_Time.md). It converts the functional requirements and acceptance criteria into deterministic test cases, expected results, and diagnostic assertions.

The design uses [SWDD_PDU_Cycle_Time.md](SWDD_PDU_Cycle_Time.md) for component boundaries and input assumptions. If a design detail conflicts with an explicit SQT requirement, the SQT requirement takes precedence.

## 2. Test Scope

### In scope

- Candidate PDU identification and CAN ID validation.
- Valid sample counting.
- Cycle-time calculation from consecutive valid samples.
- Inclusive cycle-time limit checking.
- Overall PASS/FAIL aggregation.
- Required failure diagnostics.
- Deterministic handling of malformed or unordered timestamps as described by the SWDD.

### Out of scope

- ECU firmware behavior or implementation.
- Physical CAN hardware, CANoe, HIL, flashing, and production deployment.
- AWS report publishing and other production infrastructure.
- Performance and stress testing.

Unit tests shall use in-memory observations and fixtures; they must not require CAN hardware or network access.

## 3. Test Item and Unit Boundaries

| Unit | Responsibility | Main test focus |
|---|---|---|
| Observation normalization / input adapter | Converts source records into timestamped observations and preserves source indices | Valid input, malformed input, timestamp units, ordering errors |
| PDU identification and sample selection | Selects `VehicleStatus` candidates and checks expected CAN ID | Correct ID, wrong ID, unrelated PDU ignored |
| Cycle-time calculation | Computes differences between adjacent valid sample timestamps | Exact differences, units, interval count |
| Cycle-time validator | Applies configured inclusive range | Boundaries and values outside limits |
| Result aggregator | Produces overall PASS only when all applicable checks pass | PASS case and each failure category |
| Diagnostic builder | Includes relevant failure context | Required fields for ID, sample-count, timing, and input failures |

The central evaluator may orchestrate these responsibilities, but tests should assert observable outputs rather than private implementation details. Adapter parsing tests should remain separate from evaluator tests when an adapter exists.

## 4. Test Configuration and Fixture Convention

Use the requirement values in all requirement-conformance tests:

| Setting | Value |
|---|---:|
| PDU name | `VehicleStatus` |
| Expected CAN ID | `0x180` |
| Nominal cycle time | 100 ms |
| Minimum valid sample count | 10 |
| Minimum intervals with 10 samples | 9 |
| Minimum accepted interval | 90 ms, inclusive |
| Maximum accepted interval | 110 ms, inclusive |

Represent a normalized observation conceptually as:

```text
Observation(
    timestamp=<monotonic timestamp>,
    observed_can_id=<numeric CAN ID>,
    pdu_name=<logical identity or absent>,
    source_index=<original record index>
)
```

To generate a sequence of intervals, build timestamps cumulatively from a starting timestamp. For example, ten `0x180` observations with timestamps `0, 100, 200, ..., 900 ms` contain 10 valid samples and exactly 9 measured intervals. Keep timestamps in a common high-resolution unit in production-facing tests; do not round a measured interval before limit comparison.

For a wrong-ID test, set `pdu_name` to `VehicleStatus` while setting `observed_can_id` to `0x181`. PDU identity must be independent of the observed CAN ID; an unrelated frame without that candidate identity is not evidence of a wrong-ID VehicleStatus message.

## 5. Test Case Catalogue

Each test case below is intended to be implemented as an isolated pytest test or parameterized test. Requirement cases use stable IDs to support traceability.

| Test ID | Suggested pytest name | Input / condition | Expected result and assertions | Trace |
|---|---|---|---|---|
| UTD-PDU-001 | `test_vehicle_status_nominal_timing_passes` | 10 valid `VehicleStatus` samples on ID `0x180`, spaced 100 ms apart | PASS; 10 valid samples; 9 intervals; every interval is 100 ms; no failure diagnostics | REQ-PDU-001..005 |
| UTD-PDU-002 | `test_expected_can_id_is_accepted` | Candidate PDU is `VehicleStatus` and observed ID is `0x180` | Candidate is identified as valid and counted; no ID-mismatch diagnostic | REQ-PDU-001 |
| UTD-PDU-003 | `test_wrong_can_id_fails_with_id_diagnostic` | Candidate `VehicleStatus` observed on `0x181` | FAIL; diagnostic identifies `WRONG_CAN_ID` and includes observed ID `0x181` and expected ID `0x180`; wrong-ID observation is not counted as valid | REQ-PDU-001, REQ-PDU-005, REQ-PDU-006 |
| UTD-PDU-004 | `test_ten_samples_produce_nine_cycle_intervals` | Exactly 10 valid samples with known increasing timestamps | 10 valid samples and exactly 9 cycle intervals calculated between adjacent valid samples | REQ-PDU-002, REQ-PDU-003 |
| UTD-PDU-005 | `test_minimum_sample_count_is_satisfied_at_ten` | Exactly 10 valid samples | Sample-count check passes; this check alone does not cause FAIL | REQ-PDU-002 |
| UTD-PDU-006 | `test_eight_samples_fail_with_count_diagnostic` | 8 valid samples with otherwise valid IDs and intervals | FAIL; diagnostic reports observed count 8 and required count 10 | REQ-PDU-002, REQ-PDU-005, REQ-PDU-006 |
| UTD-PDU-007 | `test_no_vehicle_status_samples_fail` | No `VehicleStatus` candidates in completed input | FAIL; reports missing/insufficient valid samples and observed count 0; must not return PASS | REQ-PDU-002, REQ-PDU-005, REQ-PDU-006 |
| UTD-PDU-008 | `test_cycle_time_uses_adjacent_valid_timestamps` | At least 10 valid samples with a deliberately varied but known sequence of allowed intervals | Calculated intervals match differences of each adjacent valid pair; intervals are not calculated against non-adjacent samples | REQ-PDU-003 |
| UTD-PDU-009 | `test_lower_cycle_time_boundary_passes` | 10 valid samples spaced exactly 90 ms apart | PASS; all 9 intervals equal 90 ms | REQ-PDU-004, REQ-PDU-005 |
| UTD-PDU-010 | `test_upper_cycle_time_boundary_passes` | 10 valid samples spaced exactly 110 ms apart | PASS; all 9 intervals equal 110 ms | REQ-PDU-004, REQ-PDU-005 |
| UTD-PDU-011 | `test_nominal_cycle_time_passes` | 10 valid samples spaced exactly 100 ms apart | PASS; all intervals equal 100 ms | REQ-PDU-004, REQ-PDU-005 |
| UTD-PDU-012 | `test_cycle_time_just_below_lower_limit_fails` | At least 2 valid samples with one interval of 89 ms; other intervals valid | FAIL; diagnostic reports 89 ms and expected range `[90, 110]` ms | REQ-PDU-004..006 |
| UTD-PDU-013 | `test_cycle_time_just_above_upper_limit_fails` | At least 2 valid samples with one interval of 111 ms; other intervals valid | FAIL; diagnostic reports 111 ms and expected range `[90, 110]` ms | REQ-PDU-004..006 |
| UTD-PDU-014 | `test_short_cycle_time_negative_example_fails` | At least 2 valid samples with one interval of 85 ms | FAIL; diagnostic includes the measured interval and allowed range | REQ-PDU-004..006 |
| UTD-PDU-015 | `test_long_cycle_time_negative_example_fails` | At least 2 valid samples with one interval of 115 ms | FAIL; diagnostic includes the measured interval and allowed range | REQ-PDU-004..006 |
| UTD-PDU-016 | `test_every_interval_is_checked` | At least 10 valid samples; one middle interval is out of range and all others are valid | FAIL; the invalid middle interval is reported even though other intervals pass | REQ-PDU-004..006 |
| UTD-PDU-017 | `test_unrelated_pdu_does_not_affect_vehicle_status` | Interleave unrelated PDU observations with 10 valid VehicleStatus samples | Unrelated frames do not change VehicleStatus valid count or its calculated intervals | REQ-PDU-001..004 |
| UTD-PDU-018 | `test_multiple_failures_are_retained` | Input includes a wrong-ID VehicleStatus candidate and an out-of-range interval among valid candidates | FAIL; diagnostics retain both applicable failure reasons and their corresponding context | REQ-PDU-005, REQ-PDU-006 |

## 6. Additional SWDD-Derived Error Cases

These cases verify robustness described by the SWDD. They supplement, but do not replace, requirement-mandated tests.

| Test ID | Suggested pytest name | Input / condition | Expected result and assertions |
|---|---|---|---|
| UTD-PDU-019 | `test_non_monotonic_timestamps_fail_without_negative_interval` | A candidate has a timestamp earlier than the preceding observation | FAIL with input-order diagnostic and source index; no negative cycle interval is accepted |
| UTD-PDU-020 | `test_invalid_timestamp_is_not_counted_as_valid_sample` | Candidate timestamp is missing or cannot be normalized | Input diagnostic includes source index; invalid observation is excluded from valid sample count |
| UTD-PDU-021 | `test_malformed_record_reports_source_index` | Adapter receives a malformed source record | Input failure diagnostic identifies the source record; malformed data is not counted as a sample |
| UTD-PDU-022 | `test_cycle_time_comparison_does_not_round_before_validation` | Use representable high-resolution timestamps whose elapsed interval is just outside a limit before display rounding | FAIL based on unrounded duration; displayed formatting must not change validation result |

## 7. Diagnostic Assertions

Assert diagnostics structurally where possible rather than matching a full rendered sentence. For each relevant failure, verify:

- A stable failure reason/category is present.
- The sample index and original source index are present when applicable.
- The associated timestamp is present when applicable.
- Wrong-ID diagnostics include observed and expected CAN IDs.
- Cycle-time diagnostics include measured time and expected inclusive range.
- Sample-count diagnostics include observed and required counts.
- The overall result is FAIL whenever at least one applicable failure exists.

Exact human-readable message wording is not part of the requirements unless the implementation defines a public message contract. Avoid brittle assertions against punctuation or full strings when structured fields are available.

## 8. Overall Result Decision Tests

Verify the aggregation behavior independently using representative evaluator outcomes:

| Condition | Expected overall status |
|---|---|
| Correct ID, at least 10 valid samples, all measured intervals within range, no other applicable failures | PASS |
| Any wrong-ID candidate for VehicleStatus | FAIL |
| Fewer than 10 valid samples | FAIL |
| Any measured interval below 90 ms or above 110 ms | FAIL |
| Multiple applicable failures | FAIL, with all safely collectable diagnostics retained |
| No matching VehicleStatus samples | FAIL |

The evaluator must not pass merely because it has no cycle intervals to check; sample presence and minimum count remain independent acceptance conditions.

## 9. Requirement Traceability Matrix

| Requirement | Unit(s) | Primary test cases |
|---|---|---|
| REQ-PDU-001 – PDU Identification | PDU identification and sample selection | UTD-PDU-001, 002, 003, 017 |
| REQ-PDU-002 – PDU Presence | Sample counting | UTD-PDU-001, 004, 005, 006, 007 |
| REQ-PDU-003 – Cycle-Time Measurement | Cycle-time calculation | UTD-PDU-004, 008 |
| REQ-PDU-004 – Cycle-Time Limits | Cycle-time validator | UTD-PDU-009 through 016 |
| REQ-PDU-005 – Overall Test Result | Result aggregator | UTD-PDU-001, 003, 006, 007, 009 through 018 |
| REQ-PDU-006 – Failure Diagnostics | Diagnostic builder and report model | UTD-PDU-003, 006, 007, 012 through 016, 018 through 021 |

## 10. Execution and Exit Criteria

- Run the focused unit tests with pytest, for example: `python -m pytest -q tests/`.
- All requirement-mandated cases in Sections 5 and 8 pass.
- All applicable failure cases return FAIL and include the required structured diagnostic data.
- Boundary tests confirm 90 ms and 110 ms pass, while 89 ms and 111 ms fail.
- No test depends on wall-clock timing, live CAN traffic, AWS, or external services.
- The test report identifies any blocked cases, unsupported input assumptions, or differences between the implemented interface and the conceptual observation model in this document.

The workspace currently contains design documents but no Python implementation or pytest suite. Test case names and the conceptual observation model are therefore proposed interfaces; align fixtures with the implemented public API when test automation is added without changing the expected behavior stated in the requirements.