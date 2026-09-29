"""Evaluate timestamped observations for the VehicleStatus cycle-time SQT."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Iterable, Optional, Union

Timestamp = Union[int, float, Decimal]


@dataclass(frozen=True)
class Observation:
    timestamp_ms: Timestamp
    observed_can_id: int
    pdu_name: str | None = "VehicleStatus"
    source_index: Optional[int] = None


@dataclass(frozen=True)
class Diagnostic:
    reason: str
    message: str
    sample_index: int | None = None
    source_index: int | None = None
    timestamp_ms: Optional[Decimal] = None
    observed_can_id: Optional[int] = None
    expected_can_id: Optional[int] = None
    measured_cycle_time_ms: Optional[Decimal] = None
    expected_cycle_time_range_ms: Optional[tuple[Decimal, Decimal]] = None
    observed_sample_count: Optional[int] = None
    required_sample_count: Optional[int] = None


@dataclass(frozen=True)
class EvaluationResult:
    passed: bool
    valid_sample_count: int
    cycle_times_ms: tuple[Decimal, ...]
    diagnostics: tuple[Diagnostic, ...]

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"


@dataclass(frozen=True)
class TestConfiguration:
    pdu_name: str = "VehicleStatus"
    expected_can_id: int = 0x180
    minimum_sample_count: int = 10
    minimum_cycle_time_ms: Decimal = Decimal("90")
    maximum_cycle_time_ms: Decimal = Decimal("110")


def _as_decimal(value: Timestamp) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError("timestamp is not a valid number") from error
    if not result.is_finite():
        raise ValueError("timestamp must be finite")
    return result


def evaluate_observations(
    observations: Iterable[Observation],
    configuration: TestConfiguration = TestConfiguration(),
) -> EvaluationResult:
    """Return a PASS only when ID, sample-count, and interval checks succeed."""
    diagnostics: list[Diagnostic] = []
    valid_samples: list[tuple[Observation, Decimal, int, int]] = []
    candidate_index = 0

    for input_index, observation in enumerate(observations, start=1):
        if observation.pdu_name != configuration.pdu_name:
            continue

        candidate_index += 1
        source_index = observation.source_index or input_index
        try:
            timestamp = _as_decimal(observation.timestamp_ms)
        except (TypeError, ValueError) as error:
            diagnostics.append(
                Diagnostic(
                    reason="INVALID_TIMESTAMP",
                    message=str(error),
                    sample_index=candidate_index,
                    source_index=source_index,
                    observed_can_id=observation.observed_can_id,
                )
            )
            continue

        if observation.observed_can_id != configuration.expected_can_id:
            diagnostics.append(
                Diagnostic(
                    reason="WRONG_CAN_ID",
                    message="VehicleStatus candidate used an unexpected CAN ID",
                    sample_index=candidate_index,
                    source_index=source_index,
                    timestamp_ms=timestamp,
                    observed_can_id=observation.observed_can_id,
                    expected_can_id=configuration.expected_can_id,
                )
            )
            continue

        if valid_samples and timestamp <= valid_samples[-1][1]:
            diagnostics.append(
                Diagnostic(
                    reason="INPUT_ORDER_ERROR",
                    message="Valid sample timestamps must increase monotonically",
                    sample_index=candidate_index,
                    source_index=source_index,
                    timestamp_ms=timestamp,
                )
            )
            continue

        valid_samples.append((observation, timestamp, candidate_index, source_index))

    cycle_times: list[Decimal] = []
    for previous, current in zip(valid_samples, valid_samples[1:]):
        _, previous_timestamp, _, _ = previous
        observation, timestamp, sample_index, source_index = current
        cycle_time = timestamp - previous_timestamp
        cycle_times.append(cycle_time)
        if not (
            configuration.minimum_cycle_time_ms
            <= cycle_time
            <= configuration.maximum_cycle_time_ms
        ):
            diagnostics.append(
                Diagnostic(
                    reason="CYCLE_TIME_OUT_OF_RANGE",
                    message="Measured cycle time is outside the allowed range",
                    sample_index=sample_index,
                    source_index=source_index,
                    timestamp_ms=timestamp,
                    measured_cycle_time_ms=cycle_time,
                    expected_cycle_time_range_ms=(
                        configuration.minimum_cycle_time_ms,
                        configuration.maximum_cycle_time_ms,
                    ),
                )
            )

    if len(valid_samples) < configuration.minimum_sample_count:
        diagnostics.append(
            Diagnostic(
                reason="INSUFFICIENT_SAMPLES",
                message="Too few valid VehicleStatus samples were received",
                observed_sample_count=len(valid_samples),
                required_sample_count=configuration.minimum_sample_count,
            )
        )

    return EvaluationResult(
        passed=not diagnostics,
        valid_sample_count=len(valid_samples),
        cycle_times_ms=tuple(cycle_times),
        diagnostics=tuple(diagnostics),
    )