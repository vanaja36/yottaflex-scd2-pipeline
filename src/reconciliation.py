
import pandas as pd
from pathlib import Path

from src.database import get_connection


def generate_reconciliation_report():

    connection = get_connection()

    # Get pipeline execution details
    query = """
        SELECT
            run_id,
            start_time,
            end_time,
            status,
            input_count,
            inserted_count,
            skipped_count,
            rejected_count,
            error_message
        FROM pipeline_runs
        ORDER BY start_time DESC
    """

    report_df = pd.read_sql_query(query, connection)

    connection.close()

    if report_df.empty:
        print("No pipeline runs available.")
        return

    # Check reconciliation
    report_df["accounted_records"] = (
        report_df["inserted_count"]
        + report_df["skipped_count"]
        + report_df["rejected_count"]
    )

    report_df["reconciliation_status"] = report_df.apply(
        lambda row: (
            "BALANCED"
            if row["input_count"] == row["accounted_records"]
            else "MISMATCH"
        ),
        axis=1
    )

    # Save report
    reports_folder = Path("reports")
    reports_folder.mkdir(parents=True, exist_ok=True)

    report_file = reports_folder / "reconciliation_report.csv"

    report_df.to_csv(report_file, index=False)

    print("\nDATA RECONCILIATION REPORT")
    print("-------------------------")

    print(report_df[[
        "input_count",
        "inserted_count",
        "skipped_count",
        "rejected_count",
        "accounted_records",
        "reconciliation_status"
    ]].to_string(index=False))

    print("\nReport saved to:", report_file)


if __name__ == "__main__":
    generate_reconciliation_report()
