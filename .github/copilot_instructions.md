# GitHub Copilot Instructions for Verify_Cycle_Time

## 1. Project name

- Project name: Verify_Cycle_Time
- Repository goal: Software Qualification Test (SQT) for validating CAN PDU cycle time behavior
- Test subject: VehicleStatus PDU transmitted on CAN ID 0x180

## 2. Description

This repository is focused on verifying the timing quality of a CAN PDU rather than implementing ECU firmware. The core validation is to confirm that the VehicleStatus message is present, correctly identified, sampled enough times, and that the measured cycle time remains within the expected range of 90 ms to 110 ms.

The project follows a training-oriented SQT workflow:

- requirement analysis
- test design
- automation
- execution
- debugging and refactoring
- reporting and CI validation

This is not a production ECU integration or manufacturing project. The goal is to demonstrate a clean, test-driven validation workflow with clear pass/fail diagnostics.

## 3. Tech stack used

- Python 3.11+
- pytest for automated testing
- GitHub Actions for CI checks
- Markdown for requirements and project documentation
- Optional CAN tooling for real capture/testing:
  - python-can
  - cantools
  - pandas/numpy for data analysis

## 4. Design pattern

Use a simple layered test design with clear separation of responsibility:

- Data acquisition layer: collect CAN samples or test data
- Validation layer: verify CAN ID, sample count, and cycle time rules
- Diagnostics layer: produce failure details such as sample index, observed ID, expected ID, and measured timing
- Reporting layer: produce PASS/FAIL outcomes based on the validation results

Testing style:

- Arrange-Act-Assert pattern
- Data-driven tests for normal, boundary, and failure cases
- Small reusable validation helpers instead of monolithic scripts
- Prefer deterministic sample data for offline validation and CI execution

## 5. Language versions and libraries

- Python: 3.11.x (preferred)
- pytest: 8.x
- python-can: 4.x (optional for real CAN capture)
- cantools: 4.x (optional for DBC-based decoding)
- pandas: 2.x (optional if CSV or time-series analysis is introduced)
- numpy: 2.x (optional for calculations)

Keep dependencies minimal. Do not introduce heavy frameworks or unnecessary runtime dependencies for this small SQT project.

## 6. Coding standards

Follow these standards in all code and tests:

- Use PEP 8 style and Pythonic naming conventions
- Write clear, descriptive function and variable names
- Add type hints to public functions where practical
- Keep functions small and focused on one responsibility
- Prefer explicit assertions with meaningful failure messages
- Use constants for expected IDs and timing limits instead of magic numbers
- Document intent only where it materially improves clarity
- Do not add test-only production code
- Ensure tests are deterministic, isolated, and repeatable
- Keep hardware-specific logic separated from core validation logic
- Treat all requirement validation as explicit business logic, not incidental behavior

## 7. Sample test code

Example pytest code for validating the VehicleStatus cycle time:

```python
import pytest

EXPECTED_CAN_ID = 0x180
MIN_SAMPLE_COUNT = 10
MIN_CYCLE_TIME_MS = 90
MAX_CYCLE_TIME_MS = 110


def calculate_cycle_times(timestamps_ms):
    return [
        b - a for a, b in zip(timestamps_ms, timestamps_ms[1:])
    ]


def validate_vehicle_status(samples):
    if not samples:
        return False, "No samples received"

    observed_ids = [sample["can_id"] for sample in samples]
    if any(can_id != EXPECTED_CAN_ID for can_id in observed_ids):
        return False, "Unexpected CAN ID detected"

    cycle_times = calculate_cycle_times([sample["timestamp_ms"] for sample in samples])
    if len(cycle_times) < MIN_SAMPLE_COUNT:
        return False, "Insufficient valid samples"

    if any(value < MIN_CYCLE_TIME_MS or value > MAX_CYCLE_TIME_MS for value in cycle_times):
        return False, "Cycle time outside allowed range"

    return True, "PASS"


def test_vehicle_status_cycle_time_pass_case():
    samples = [
        {"can_id": 0x180, "timestamp_ms": 0},
        {"can_id": 0x180, "timestamp_ms": 100},
        {"can_id": 0x180, "timestamp_ms": 200},
        {"can_id": 0x180, "timestamp_ms": 300},
        {"can_id": 0x180, "timestamp_ms": 400},
        {"can_id": 0x180, "timestamp_ms": 500},
        {"can_id": 0x180, "timestamp_ms": 600},
        {"can_id": 0x180, "timestamp_ms": 700},
        {"can_id": 0x180, "timestamp_ms": 800},
        {"can_id": 0x180, "timestamp_ms": 900},
        {"can_id": 0x180, "timestamp_ms": 1000},
    ]

    ok, result = validate_vehicle_status(samples)
    assert ok is True, result


def test_vehicle_status_cycle_time_fail_case():
    samples = [
        {"can_id": 0x180, "timestamp_ms": 0},
        {"can_id": 0x180, "timestamp_ms": 85},
        {"can_id": 0x180, "timestamp_ms": 170},
        {"can_id": 0x180, "timestamp_ms": 255},
    ]

    ok, result = validate_vehicle_status(samples)
    assert ok is False
    assert "Cycle time outside allowed range" in result or "Insufficient valid samples" in result
```

## 8. Folder structure

Suggested repository layout:

```text
Verify_Cycle_Time/
├── .github/
│   └── copilot_instructions.md
├── docs/
│   └── SQT_REQUIREMENTS_PDU_Cycle_Time.md
├── src/
│   ├── __init__.py
│   ├── cycle_time_validator.py
│   ├── can_reader.py
│   └── reporting.py
├── tests/
│   ├── test_cycle_time_validation.py
│   ├── test_boundary_cases.py
│   └── test_negative_cases.py
├── config/
│   └── settings.example.json
├── .env.example
├── README.md
├── requirements.txt
└── pytest.ini
```

## 9. Sensitive data handling

- Do not commit production secrets, ECU credentials, CAN logs with personal or sensitive content, or any private infrastructure values
- Store keys, tokens, or environment-specific settings in environment variables or local configuration files that are excluded from version control
- Use placeholders in example files such as `.env.example`
- Keep diagnostic logs focused on test metadata such as CAN ID, sample index, and timestamp values only
- Redact or omit any personally identifiable information or proprietary identifiers before publishing logs or screenshots
- Ensure no credentials, API keys, or internal URLs are included in code comments, markdown, or test artifacts
- Before merging, review diffs for accidental persistence of secrets or confidential data

## 10. Additional guidance

- Keep the project aligned to the requirement document in [docs/SQT_REQUIREMENTS_PDU_Cycle_Time.md](docs/SQT_REQUIREMENTS_PDU_Cycle_Time.md)
- Treat PASS/FAIL outcomes as explicit business logic with clear diagnostic output
- Prefer test cases that validate boundary conditions and negative scenarios as well as nominal behavior
- Keep automation simple, readable, and maintainable for training and learning purposes
- Do not expand the scope into ECU firmware development or production hardware integration unless explicitly requested
- If optional reporting is added, keep it separate from the core validation logic and clearly label it as a training extension

## 11. Expected behavior summary

The implementation should validate the following:

- PDU is present
- CAN ID matches 0x180
- At least 10 valid samples are available
- Consecutive timestamps can be converted to cycle times
- Every measured cycle time is within the valid range 90 ms to 110 ms
- Failures provide enough detail to diagnose the issue
- Overall result is PASS only when all applicable requirements succeed
