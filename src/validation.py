
import pandas as pd

REQUIRED_COLUMNS = [
    "customer_id",
    "customer_name",
    "city",
    "effective_date",
    "event_id"
]


def validate_customer_data(df):

    valid_records = []
    rejected_records = []

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # Track event IDs already encountered in this batch
    seen_event_ids = set()

    for _, row in df.iterrows():

        errors = []

        # Check missing values
        for column in REQUIRED_COLUMNS:
            if pd.isna(row[column]) or str(row[column]).strip() == "":
                errors.append(f"Missing {column}")

        # Check date format
        if not pd.isna(row["effective_date"]):
            try:
                parsed_date = pd.to_datetime(
                    row["effective_date"],
                    format="%Y-%m-%d",
                    errors="raise"
                )

                # Require exact YYYY-MM-DD format
                if parsed_date.strftime("%Y-%m-%d") != str(row["effective_date"]).strip():
                    errors.append("Invalid effective_date")

            except (ValueError, TypeError):
                errors.append("Invalid effective_date")

        # Check duplicate event IDs within this batch
        event_id = str(row["event_id"]).strip()

        if event_id and event_id in seen_event_ids:
            errors.append("Duplicate event_id")
        elif event_id:
            seen_event_ids.add(event_id)

        # Separate valid and rejected records
        if errors:
            rejected_row = row.to_dict()
            rejected_row["rejection_reason"] = "; ".join(errors)
            rejected_records.append(rejected_row)
        else:
            valid_records.append(row.to_dict())

    return (
        pd.DataFrame(valid_records, columns=df.columns),
        pd.DataFrame(rejected_records)
    )
