"""Row allocation: --records must be the exact number of generated entries.

`--records` is the total observation count for the cohort. It may change how many
patients are created, but it must never change the days-per-patient duration that
the config (or --days) establishes, and it must never override an explicit
--patients / --days request.
"""

import pytest

from app.modules.generate import allocate_days


def test_records_is_the_exact_number_of_rows():
    counts = allocate_days(records=1000, default_days=60)
    assert sum(counts) == 1000


def test_full_patients_keep_the_configured_duration_and_the_last_one_takes_the_rest():
    counts = allocate_days(records=1000, default_days=60)
    assert counts[:-1] == [60] * 16
    assert counts[-1] == 40
    assert len(counts) == 17


def test_an_exact_multiple_leaves_no_partial_patient():
    assert allocate_days(records=120, default_days=60) == [60, 60]


def test_small_request_does_not_explode_into_one_patient_per_row():
    """Antes: --records 100 daba 100 pacientes × 60 días = 6000 filas."""
    counts = allocate_days(records=100, default_days=60)
    assert sum(counts) == 100
    assert len(counts) == 2


def test_fewer_records_than_one_duration_gives_one_shorter_patient():
    assert allocate_days(records=30, default_days=60) == [30]


def test_explicit_patients_wins_over_records():
    counts = allocate_days(records=1000, patients=4, default_days=60)
    assert counts == [60, 60, 60, 60]


def test_explicit_patients_and_days_are_respected_as_given():
    assert allocate_days(records=1000, patients=4, days=10) == [10] * 4


def test_explicit_days_keeps_that_duration_and_records_still_exact():
    counts = allocate_days(records=100, days=30)
    assert counts == [30, 30, 30, 10]
    assert sum(counts) == 100


@pytest.mark.parametrize("records", [0, -5])
def test_records_must_be_at_least_one(records):
    with pytest.raises(ValueError, match="records"):
        allocate_days(records=records, default_days=60)


@pytest.mark.parametrize("days", [0, -1])
def test_days_must_be_at_least_one(days):
    with pytest.raises(ValueError, match="days"):
        allocate_days(records=100, days=days)


def test_patients_must_be_at_least_one():
    with pytest.raises(ValueError, match="patients"):
        allocate_days(records=100, patients=0)
