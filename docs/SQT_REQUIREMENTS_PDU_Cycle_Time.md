# Software Qualification Test Requirements

## System Under Test

ECU transmitting a periodic CAN PDU.

### PDU Under Test

- **PDU Name:** VehicleStatus
- **CAN ID:** `0x180`
- **Expected Cycle Time:** `100 ms`
- **Allowed Tolerance:** `±10 ms`
- **Valid Cycle-Time Range:** `90 ms to 110 ms`
- **Minimum Required Samples:** `10`

---

## Functional Requirements

### REQ-PDU-001 – PDU Identification

The software qualification test shall verify that the ECU transmits the **VehicleStatus PDU** using CAN ID `0x180`.

### REQ-PDU-002 – PDU Presence

The software qualification test shall detect at least **10 valid VehicleStatus PDU messages** during the observation window.

### REQ-PDU-003 – Cycle-Time Measurement

The software qualification test shall calculate the cycle time using the timestamp difference between two consecutive valid VehicleStatus PDU messages.

### REQ-PDU-004 – Cycle-Time Limits

Each measured VehicleStatus PDU cycle time shall be within the range:

**90 ms ≤ Cycle Time ≤ 110 ms**

A cycle time outside this range shall be considered a test failure.

### REQ-PDU-005 – Overall Test Result

The qualification test shall report **PASS** only when all applicable PDU identification, PDU presence, and cycle-time requirements are satisfied.

If any applicable requirement fails, the overall test result shall be **FAIL**.

### REQ-PDU-006 – Failure Diagnostics

For every test failure, the qualification test shall provide sufficient diagnostic information to identify the failure.

The diagnostic information shall include, where applicable:

- Message/sample index
- Timestamp
- Observed CAN ID
- Expected CAN ID
- Measured cycle time
- Expected cycle-time range
- Reason for failure

---

## Test Acceptance Criteria

The test shall be considered **PASS** when all of the following conditions are satisfied:

1. VehicleStatus PDU is received.
2. CAN ID is `0x180`.
3. At least 10 valid PDU samples are available.
4. Cycle time can be calculated between consecutive valid PDU samples.
5. Every measured cycle time is between 90 ms and 110 ms.
6. No applicable requirement reports a failure.

---

## Negative Test Conditions

The qualification test shall also verify that it can detect:

### Negative Condition 1 – Wrong CAN ID

Example:

- Expected CAN ID: `0x180`
- Observed CAN ID: `0x181`

Expected result: **FAIL**

### Negative Condition 2 – Short Cycle Time

Example:

- Expected cycle time: `100 ms`
- Observed cycle time: `85 ms`

Expected result: **FAIL**

### Negative Condition 3 – Long Cycle Time

Example:

- Expected cycle time: `100 ms`
- Observed cycle time: `115 ms`

Expected result: **FAIL**

### Negative Condition 4 – Insufficient Samples

Example:

- Required samples: `10`
- Observed valid samples: `8`

Expected result: **FAIL**

---

## Boundary Conditions

The following boundary values shall be tested:

| Condition | Cycle Time | Expected Result |
|---|---:|---|
| Lower boundary | 90 ms | PASS |
| Nominal | 100 ms | PASS |
| Upper boundary | 110 ms | PASS |
| Just below lower limit | 89 ms | FAIL |
| Just above upper limit | 111 ms | FAIL |

---

## Traceability

| Requirement | Test Coverage |
|---|---|
| REQ-PDU-001 | CAN ID validation |
| REQ-PDU-002 | Minimum sample-count validation |
| REQ-PDU-003 | Cycle-time calculation |
| REQ-PDU-004 | Cycle-time range validation |
| REQ-PDU-005 | Overall PASS/FAIL determination |
| REQ-PDU-006 | Failure diagnostic reporting |

---

## Out of Scope for This MVP

The following activities are intentionally excluded because this is a **Software Qualification Testing** training exercise:

- ECU software implementation
- ECU software architecture
- ECU firmware development
- ECU flashing/programming
- CANoe hardware integration
- Hardware-in-the-loop testing
- Production ECU deployment
- Production AWS infrastructure
- Production security/authentication

AWS may be included only as an **optional training extension** for publishing automated test reports.

---

## Training Objective

The requirements are intentionally simple so that the complete GitHub Copilot-assisted testing workflow can be demonstrated:

**Requirement Analysis → Test Design → Test Automation → Test Execution → Debugging → Refactoring → Code Review → CI/CD → Optional AWS Report Publishing**
