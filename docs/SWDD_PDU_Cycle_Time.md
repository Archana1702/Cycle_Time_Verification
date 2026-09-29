# Software Design Description: PDU Cycle-Time Qualification Test

## 1. Purpose

This document describes the software design for the qualification test specified in [SQT_REQUIREMENTS_PDU_Cycle_Time.md](SQT_REQUIREMENTS_PDU_Cycle_Time.md). The software evaluates timestamped CAN observations and produces a PASS or FAIL result with diagnostics. It does not implement ECU behavior.

## 2. Scope

### In scope

- Identify observations associated with the configured `VehicleStatus` PDU.
- Verify the expected CAN ID (`0x180`).
- Count valid PDU samples and require at least 10.
- Calculate intervals between consecutive valid samples.
- Accept inclusive cycle-time limits of 90 ms through 110 ms.
- Produce an overall result and actionable failure diagnostics.
- Support deterministic automated tests for negative and boundary conditions.

### Out of scope

ECU firmware, ECU architecture, ECU flashing, CANoe hardware integration, hardware-in-the-loop testing, production deployment, production security, and production AWS infrastructure are excluded. A live CAN adapter and optional report publishing may be added later without changing the evaluation rules.

## 3. Design Inputs and Decisions

| Item | Design decision |
|---|---|
| PDU name | `VehicleStatus` |
| Expected CAN ID | `0x180` |
| Nominal cycle time | 100 ms |
| Accepted interval | Inclusive range `[90 ms, 110 ms]` |
| Minimum valid samples | 10 |
| Minimum intervals at 10 samples | 9, each calculated from adjacent valid samples |
| Time unit | Normalize timestamps to integer microseconds (or finer source precision) before subtraction; report in milliseconds |
| Test input | Timestamped observations supplied through an input adapter; deterministic fixture/trace input is the MVP source |
| Result rule | PASS only when all applicable identification, presence, and interval checks pass |

The input must preserve PDU identity independently of the observed CAN ID. A raw CAN identifier cannot, by itself, establish that a frame with ID `0x181` was intended to be `VehicleStatus`. The adapter or fixture therefore supplies a candidate PDU name from a test label or configured message mapping. The evaluator compares that candidate's observed ID with the expected ID. Without such identity metadata, a wrong-ID case is reported as a missing expected PDU, not conclusively as a wrong-ID VehicleStatus frame.

## 4. System Context

```text
Timestamped CAN source / deterministic fixture
                    |
                    v
              Input adapter
                    |
                    v
              Test evaluator <--- PDU test configuration
                    |
             +------+------+
             v             v
       Test result      Diagnostics
             |
             v
       Report renderer
```

The adapter is responsible for parsing the source and providing normalized observations. The evaluator owns all qualification decisions and does not depend on a specific CAN tool or report format.

## 5. Components

### 5.1 Input Adapter

Reads a deterministic trace or fixture and emits observations in timestamp order. Each observation contains:

| Field | Type / meaning |
|---|---|
| `timestamp` | Monotonic receive timestamp with source precision and unit |
| `observed_can_id` | Numeric CAN identifier |
| `pdu_name` | Logical PDU identity from fixture label or configured message mapping; may be absent for unrelated frames |
| `source_index` | Original record index for diagnostics |

The adapter rejects malformed records and timestamps that cannot be normalized. It preserves source indices and does not silently sort or discard input; ordering errors are surfaced as input failures. Unrelated frames may be ignored by the evaluator.

### 5.2 Test Configuration

Provides the PDU name, expected CAN ID, minimum valid sample count, lower and upper cycle-time bounds, and optional observation timeout. MVP defaults are `VehicleStatus`, `0x180`, 10, 90 ms, and 110 ms. Values are configurable to enable reuse, but tests for this requirement set must use those values.

### 5.3 Test Evaluator

Consumes candidate observations and configuration. For each observation labeled `VehicleStatus`, it:

1. Records a CAN-ID mismatch if the observed ID differs from `0x180`.
2. Counts the observation as a valid sample only when its CAN ID matches `0x180` and its timestamp is valid.
3. Calculates the cycle time from each valid sample to the immediately preceding valid sample.
4. Records a failure when any measured cycle time is below 90 ms or above 110 ms. Exact values of 90 ms and 110 ms pass.
5. After input completion or observation timeout, records insufficient-sample failure if fewer than 10 valid samples were collected.
6. Returns PASS only if no applicable check failed.

Wrong-ID candidates are diagnosed but excluded from the valid-sample count and cycle calculation. This keeps the meaning of “valid PDU sample” consistent with successful PDU identification.

### 5.4 Result and Diagnostic Model

The evaluator returns one test result with an overall status, counts, measured intervals, and zero or more diagnostics. Each diagnostic includes applicable fields from this set:

| Field | Description |
|---|---|
| `reason` | Stable failure category, such as `WRONG_CAN_ID`, `INSUFFICIENT_SAMPLES`, `CYCLE_TIME_OUT_OF_RANGE`, `INVALID_TIMESTAMP`, or `INPUT_ORDER_ERROR` |
| `sample_index` | One-based candidate or valid-sample index, as applicable |
| `source_index` | Original input record index |
| `timestamp` | Timestamp associated with the failure |
| `observed_can_id` | Observed ID, when available |
| `expected_can_id` | `0x180`, when the ID check applies |
| `measured_cycle_time_ms` | Measured interval, when calculable |
| `expected_cycle_time_range_ms` | `[90, 110]`, when the interval check applies |
| `observed_sample_count` | Valid sample count, for sample-count failure |
| `required_sample_count` | 10, for sample-count failure |
| `message` | Human-readable explanation |

The report renderer formats this model for console, JSON, or another selected output. Formatting must not change the evaluator's result.

## 6. Processing and Result Logic

For ordered valid samples with timestamps $t_1, t_2, \ldots, t_n$, each measured interval is:

$$
\Delta t_i = t_i - t_{i-1}, \quad 2 \leq i \leq n
$$

Convert timestamps to a common high-resolution unit before subtraction, then convert the difference to milliseconds for limit checking and reporting. Do not round before comparing with the limits. A test passes its interval check exactly when:

$$
90\,\text{ms} \leq \Delta t_i \leq 110\,\text{ms}
$$

At least 10 valid samples are required; those samples provide 9 measured intervals. If fewer than two valid samples exist, no interval can be calculated and the sample-count check fails. For any two or more valid samples, all resulting intervals are checked, even when the final count is below 10; the test can therefore report both interval violations and insufficient samples.

Overall status is FAIL if any applicable check fails; otherwise it is PASS. A test with no matching candidates fails the sample-count requirement and reports that no valid `VehicleStatus` sample was observed.

## 7. Interfaces

### Observation stream interface

The adapter supplies a sequence of observations and an explicit end-of-input or timeout event. Adapter-specific parsing stays outside the evaluator.

### Evaluator interface

Conceptual interface (language-neutral):

```text
evaluate(observations, pdu_test_configuration) -> test_result
```

The evaluator is deterministic: identical normalized observations and configuration produce an identical result and diagnostics.

### Report interface

The report renderer accepts `test_result` and emits a human-readable report. A machine-readable JSON representation is recommended for CI integration, but is not required to evaluate or pass the MVP test.

## 8. Error Handling

- Malformed source records: emit an input diagnostic with source index; do not treat malformed data as a valid PDU sample.
- Non-monotonic timestamps: emit an input-order diagnostic and fail the run; do not compute a negative or ambiguous interval.
- Wrong CAN ID for a labeled candidate: report observed and expected IDs; exclude it from valid count and interval calculation.
- No candidates or fewer than 10 valid samples: fail with observed and required counts.
- Out-of-range interval: report adjacent sample indices/timestamps, measured interval, and inclusive expected range.
- Adapter or file I/O failure: return FAIL with an input-source diagnostic rather than a PASS or an unhandled success state.

Where processing can safely continue, collect multiple diagnostics in one run to make failures easier to debug.

## 9. Verification Design

The evaluator is tested independently of any CAN hardware using timestamped fixtures. Required cases:

| Case | Input | Expected result |
|---|---|---|
| Correct PDU and nominal timing | ID `0x180`, at least 10 valid samples spaced 100 ms apart | PASS |
| Lower boundary | Every measured interval is 90 ms | PASS |
| Upper boundary | Every measured interval is 110 ms | PASS |
| Below lower boundary | One measured interval is 89 ms | FAIL with measured interval diagnostic |
| Above upper boundary | One measured interval is 111 ms | FAIL with measured interval diagnostic |
| Short-cycle negative example | One measured interval is 85 ms | FAIL |
| Long-cycle negative example | One measured interval is 115 ms | FAIL |
| Wrong CAN ID | `VehicleStatus` candidate observed as ID `0x181` | FAIL with observed and expected IDs |
| Insufficient samples | 8 correctly identified samples | FAIL with observed count 8 and required count 10 |
| No matching PDU | No `VehicleStatus` candidates | FAIL with missing/insufficient-sample diagnostic |
| Multiple failures | Wrong ID and out-of-range valid interval in the same input | FAIL and retain both applicable diagnostics |

Tests should also verify that exactly 10 valid samples produce 9 intervals, comparison limits are inclusive and unrounded, and unrelated PDU frames do not affect the VehicleStatus count or timing.

## 10. Requirement Traceability

| Requirement | Design element | Verification |
|---|---|---|
| REQ-PDU-001 | Candidate identity and expected-ID comparison in Test Evaluator | Correct-ID and wrong-ID fixtures |
| REQ-PDU-002 | Valid-sample counter and minimum sample check | 10-sample, 8-sample, and no-sample fixtures |
| REQ-PDU-003 | Adjacent valid-sample timestamp subtraction | Nominal timing and interval-count checks |
| REQ-PDU-004 | Inclusive 90-110 ms range comparison | 90, 110, 89, and 111 ms fixtures |
| REQ-PDU-005 | Overall result aggregation | PASS case and single-/multiple-failure cases |
| REQ-PDU-006 | Structured Diagnostic Model and report renderer | Assert diagnostic fields for each failure category |

## 11. Assumptions and Open Design Inputs

- A trace or fixture can associate a logical PDU name with observations, including wrong-ID examples. If a future live source cannot provide this identity, wrong IDs can only be inferred through a configured alternative-ID mapping or reported as missing expected traffic.
- The observation window ends when the input is exhausted or an optional timeout is reached. A concrete timeout value is not specified by the requirements and must be selected by the runner when using a live source.
- Timestamps represent receive times from a consistent monotonic clock. Wall-clock timestamps may be retained for display but must not be used for elapsed-time calculation if they can jump.
- The requirements do not specify CAN FD or extended-ID handling. The MVP should preserve the source identifier format and compare the numeric ID according to the selected trace format; support for additional CAN frame attributes can be added when needed.

## 12. Training Workflow Fit

This design supports the stated workflow: requirements map to deterministic test cases; the evaluator can be automated and run in CI; failed assertions carry diagnostic context for debugging; and the report interface can be extended for optional AWS publishing without making AWS part of the MVP.