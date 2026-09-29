import csv
from decimal import Decimal
from pathlib import Path

import pytest

from src.cycle_time_validator import Observation, evaluate_observations


EXPECTED_CAN_ID = 0x180
PDU_NAME = "VehicleStatus"
CSV_PATH = Path(__file__).parents[1] / "docs" / "unit-test-design.csv"


def observations_with_intervals(intervals_ms, can_id=EXPECTED_CAN_ID):
    """Build a PDU sample sequence from consecutive interval durations."""
    timestamps = [Decimal("0")]
    for interval_ms in intervals_ms:
        timestamps.append(timestamps[-1] + Decimal(str(interval_ms)))
    return [
        Observation(
            timestamp_ms=timestamp,
            observed_can_id=can_id,
            pdu_name=PDU_NAME,
            source_index=index,
        )
        for index, timestamp in enumerate(timestamps, start=1)
    ]


def steady_observations(interval_ms=100, sample_count=10):
    return observations_with_intervals([interval_ms] * (sample_count - 1))


def test_vehicle_status_nominal_cycle_time_passes():
    result = evaluate_observations(steady_observations())

    assert result.status == "PASS"
    assert result.valid_sample_count == 10
    assert len(result.cycle_times_ms) == 9
    assert result.cycle_times_ms == (Decimal("100"),) * 9
    assert result.diagnostics == ()


def test_vehicle_status_expected_can_id_is_accepted():
    result = evaluate_observations(steady_observations())

    assert result.valid_sample_count == 10
    assert all(item.reason != "WRONG_CAN_ID" for item in result.diagnostics)


def test_vehicle_status_wrong_can_id_fails():
    samples = steady_observations()
    samples[0] = Observation(0, 0x181, PDU_NAME, source_index=1)
    result = evaluate_observations(samples)

    assert result.status == "FAIL"
    diagnostic = next(item for item in result.diagnostics if item.reason == "WRONG_CAN_ID")
    assert diagnostic.observed_can_id == 0x181
    assert diagnostic.expected_can_id == EXPECTED_CAN_ID
    assert diagnostic.sample_index == 1
    assert diagnostic.source_index == 1
    assert diagnostic.timestamp_ms == Decimal("0")


def test_minimum_sample_count_of_ten_passes():
    result = evaluate_observations(steady_observations(sample_count=10))

    assert result.valid_sample_count == 10
    assert all(item.reason != "INSUFFICIENT_SAMPLES" for item in result.diagnostics)


def test_eight_valid_samples_fail_sample_requirement():
    result = evaluate_observations(steady_observations(sample_count=8))

    assert result.status == "FAIL"
    diagnostic = next(item for item in result.diagnostics if item.reason == "INSUFFICIENT_SAMPLES")
    assert diagnostic.observed_sample_count == 8
    assert diagnostic.required_sample_count == 10


def test_cycle_time_is_calculated_between_consecutive_messages():
    result = evaluate_observations(observations_with_intervals([100]))

    assert result.cycle_times_ms == (Decimal("100"),)
    assert result.valid_sample_count == 2
    assert result.status == "FAIL"  # The SQT still requires at least 10 samples.


@pytest.mark.parametrize("interval_ms", [90, 100, 110])
def test_cycle_time_accepted_values(interval_ms):
    result = evaluate_observations(steady_observations(interval_ms=interval_ms))

    assert result.status == "PASS"
    assert result.cycle_times_ms == (Decimal(str(interval_ms)),) * 9


def test_lower_cycle_time_boundary_90_ms_passes():
    assert evaluate_observations(steady_observations(90)).status == "PASS"


def test_nominal_cycle_time_100_ms_passes():
    assert evaluate_observations(steady_observations(100)).status == "PASS"


def test_upper_cycle_time_boundary_110_ms_passes():
    assert evaluate_observations(steady_observations(110)).status == "PASS"


def assert_cycle_time_below_limit_fails(interval_ms):
    samples = observations_with_intervals([100] * 4 + [interval_ms] + [100] * 4)
    result = evaluate_observations(samples)

    assert result.status == "FAIL"
    diagnostic = next(
        item for item in result.diagnostics
        if item.reason == "CYCLE_TIME_OUT_OF_RANGE"
    )
    assert diagnostic.measured_cycle_time_ms == Decimal(str(interval_ms))
    assert diagnostic.expected_cycle_time_range_ms == (Decimal("90"), Decimal("110"))
    assert diagnostic.sample_index == 6
    assert diagnostic.source_index == 6
    assert diagnostic.timestamp_ms == sum(
        (Decimal(str(value)) for value in [100] * 4 + [interval_ms]), Decimal("0")
    )


def test_cycle_time_89_ms_fails_lower_limit():
    assert_cycle_time_below_limit_fails(89)


def test_short_cycle_time_85_ms_fails():
    assert_cycle_time_below_limit_fails(85)


def assert_cycle_time_above_limit_fails(interval_ms):
    samples = observations_with_intervals([100] * 4 + [interval_ms] + [100] * 4)
    result = evaluate_observations(samples)

    assert result.status == "FAIL"
    diagnostic = next(
        item for item in result.diagnostics
        if item.reason == "CYCLE_TIME_OUT_OF_RANGE"
    )
    assert diagnostic.measured_cycle_time_ms == Decimal(str(interval_ms))
    assert diagnostic.expected_cycle_time_range_ms == (Decimal("90"), Decimal("110"))


def test_cycle_time_111_ms_fails_upper_limit():
    assert_cycle_time_above_limit_fails(111)


def test_long_cycle_time_115_ms_fails():
    assert_cycle_time_above_limit_fails(115)


def test_any_out_of_range_interval_fails_overall_result():
    samples = observations_with_intervals([100] * 4 + [85] + [100] * 4)
    result = evaluate_observations(samples)

    assert result.status == "FAIL"
    assert len([d for d in result.diagnostics if d.reason == "CYCLE_TIME_OUT_OF_RANGE"]) == 1


def test_overall_result_passes_only_when_all_requirements_pass():
    passing = evaluate_observations(steady_observations())
    wrong_id = steady_observations()
    wrong_id[0] = Observation(0, 0x181, PDU_NAME, source_index=1)
    insufficient = evaluate_observations(steady_observations(sample_count=8))
    bad_timing = evaluate_observations(
        observations_with_intervals([100] * 4 + [85] + [100] * 4)
    )

    assert passing.status == "PASS"
    assert evaluate_observations(wrong_id).status == "FAIL"
    assert insufficient.status == "FAIL"
    assert bad_timing.status == "FAIL"


def test_failure_diagnostics_include_applicable_context():
    wrong_id = steady_observations()
    wrong_id[0] = Observation(0, 0x181, PDU_NAME, source_index=1)
    wrong_id_result = evaluate_observations(wrong_id)
    count_result = evaluate_observations(steady_observations(sample_count=8))
    timing_result = evaluate_observations(observations_with_intervals([85]))

    id_diagnostic = next(d for d in wrong_id_result.diagnostics if d.reason == "WRONG_CAN_ID")
    count_diagnostic = next(d for d in count_result.diagnostics if d.reason == "INSUFFICIENT_SAMPLES")
    timing_diagnostic = next(d for d in timing_result.diagnostics if d.reason == "CYCLE_TIME_OUT_OF_RANGE")

    assert id_diagnostic.observed_can_id == 0x181
    assert id_diagnostic.expected_can_id == EXPECTED_CAN_ID
    assert id_diagnostic.timestamp_ms == Decimal("0")
    assert count_diagnostic.observed_sample_count == 8
    assert count_diagnostic.required_sample_count == 10
    assert timing_diagnostic.measured_cycle_time_ms == Decimal("85")
    assert timing_diagnostic.expected_cycle_time_range_ms == (Decimal("90"), Decimal("110"))
    assert timing_diagnostic.sample_index is not None
    assert timing_diagnostic.timestamp_ms == Decimal("85")


def test_csv_test_case_names_are_covered_by_test_script():
    with CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
        csv_case_names = {row["test_case_name"] for row in csv.DictReader(csv_file)}

    implemented_test_names = {
        "test_vehicle_status_nominal_cycle_time_passes",
        "test_vehicle_status_expected_can_id_is_accepted",
        "test_vehicle_status_wrong_can_id_fails",
        "test_minimum_sample_count_of_ten_passes",
        "test_eight_valid_samples_fail_sample_requirement",
        "test_cycle_time_is_calculated_between_consecutive_messages",
        "test_lower_cycle_time_boundary_90_ms_passes",
        "test_nominal_cycle_time_100_ms_passes",
        "test_upper_cycle_time_boundary_110_ms_passes",
        "test_cycle_time_89_ms_fails_lower_limit",
        "test_cycle_time_111_ms_fails_upper_limit",
        "test_short_cycle_time_85_ms_fails",
        "test_long_cycle_time_115_ms_fails",
        "test_any_out_of_range_interval_fails_overall_result",
        "test_overall_result_passes_only_when_all_requirements_pass",
        "test_failure_diagnostics_include_applicable_context",
    }

    assert csv_case_names == implemented_test_names
