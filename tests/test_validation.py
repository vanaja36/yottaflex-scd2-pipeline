
import pandas as pd
import pytest

from src.validation import validate_customer_data


COLUMNS = [
    "customer_id",
    "customer_name",
    "city",
    "effective_date",
    "event_id"
]


def test_valid_and_invalid_records():

    data = [
        ["C101", "Ravi", "Hyderabad", "2026-01-01", "E101"],
        ["C102", "Priya", "Vijayawada", "2026-01-02", "E102"],
        ["C103", "Kumar", "", "2026-01-03", "E103"],
        ["", "Anjali", "Chennai", "2026-01-04", "E104"],
        ["C104", "Arjun", "Bangalore", "invalid-date", "E105"]
    ]

    df = pd.DataFrame(data, columns=COLUMNS)

    valid_df, rejected_df = validate_customer_data(df)

    assert len(valid_df) == 2
    assert len(rejected_df) == 3


def test_empty_input():

    df = pd.DataFrame(columns=COLUMNS)

    valid_df, rejected_df = validate_customer_data(df)

    assert len(valid_df) == 0
    assert len(rejected_df) == 0


def test_duplicate_event_id():

    data = [
        ["C101", "Ravi", "Hyderabad", "2026-01-01", "E101"],
        ["C102", "Priya", "Vijayawada", "2026-01-02", "E102"],
        ["C103", "Kumar", "Chennai", "2026-01-03", "E101"]
    ]

    df = pd.DataFrame(data, columns=COLUMNS)

    valid_df, rejected_df = validate_customer_data(df)

    assert len(valid_df) == 2
    assert len(rejected_df) == 1
    assert "Duplicate event_id" in rejected_df.iloc[0]["rejection_reason"]


def test_missing_required_column():

    df = pd.DataFrame({
        "customer_id": ["C101"],
        "customer_name": ["Ravi"],
        "city": ["Hyderabad"],
        "effective_date": ["2026-01-01"]
    })

    with pytest.raises(ValueError, match="Missing columns"):
        validate_customer_data(df)


def test_missing_customer_id():

    data = [
        ["", "Ravi", "Hyderabad", "2026-01-01", "E101"]
    ]

    df = pd.DataFrame(data, columns=COLUMNS)

    valid_df, rejected_df = validate_customer_data(df)

    assert len(valid_df) == 0
    assert len(rejected_df) == 1
    assert "Missing customer_id" in rejected_df.iloc[0]["rejection_reason"]


def test_invalid_date_format():

    data = [
        ["C101", "Ravi", "Hyderabad", "01-31-2026", "E101"]
    ]

    df = pd.DataFrame(data, columns=COLUMNS)

    valid_df, rejected_df = validate_customer_data(df)

    assert len(valid_df) == 0
    assert len(rejected_df) == 1
    assert "Invalid effective_date" in rejected_df.iloc[0]["rejection_reason"]
