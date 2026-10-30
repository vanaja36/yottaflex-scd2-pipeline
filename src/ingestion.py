

import pandas as pd
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone

from src.database import get_connection
from src.validation import validate_customer_data


def ingest_customer_data(file_path):

    run_id = str(uuid.uuid4())
    start_time = datetime.now(timezone.utc).isoformat()

    print(f"Starting ingestion. Run ID: {run_id}")

    connection = get_connection()

    input_count = 0
    inserted_count = 0
    skipped_count = 0
    rejected_count = 0

    try:
        # Step 1: Register this pipeline run
        connection.execute("""
            INSERT INTO pipeline_runs (
                run_id, start_time, status
            )
            VALUES (?, ?, ?)
        """, (run_id, start_time, "RUNNING"))

        connection.commit()

        # Step 2: Read input file
        df = pd.read_csv(file_path)
        input_count = len(df)

        # Step 3: Validate records
        valid_df, rejected_df = validate_customer_data(df)
        rejected_count = len(rejected_df)

        # Step 4: Add metadata
        valid_df = valid_df.copy()
        rejected_df = rejected_df.copy()

        valid_df["source_file"] = Path(file_path).name
        valid_df["run_id"] = run_id

        rejected_df["source_file"] = Path(file_path).name
        rejected_df["run_id"] = run_id

        # Step 5: Save rejected records
        rejected_folder = Path("data/rejected")
        rejected_folder.mkdir(parents=True, exist_ok=True)

        if not rejected_df.empty:
            rejected_file = rejected_folder / f"rejected_{run_id}.csv"
            rejected_df.to_csv(rejected_file, index=False)
            print(f"Rejected records saved to: {rejected_file}")

        # Step 6: Detect existing event IDs
        existing_ids = pd.read_sql_query(
            "SELECT event_id FROM customer_events",
            connection
        )["event_id"].tolist()

        new_df = valid_df[
            ~valid_df["event_id"].isin(existing_ids)
        ].copy()

        skipped_count = len(valid_df) - len(new_df)

        # Step 7: Insert only new records
        if not new_df.empty:
            new_df.to_sql(
                "customer_events",
                connection,
                if_exists="append",
                index=False
            )

        inserted_count = len(new_df)

        # Step 8: Mark run successful and save metrics
        end_time = datetime.now(timezone.utc).isoformat()

        connection.execute("""
            UPDATE pipeline_runs
            SET end_time = ?,
                status = ?,
                input_count = ?,
                inserted_count = ?,
                skipped_count = ?,
                rejected_count = ?
            WHERE run_id = ?
        """, (
            end_time,
            "SUCCESS",
            input_count,
            inserted_count,
            skipped_count,
            rejected_count,
            run_id
        ))

        connection.commit()

        print("\nIngestion Summary")
        print("-----------------")
        print("Total records:", input_count)
        print("Inserted records:", inserted_count)
        print("Skipped duplicates:", skipped_count)
        print("Rejected records:", rejected_count)
        print("Status: SUCCESS")
        print("Run ID:", run_id)

    except Exception as error:

        connection.rollback()

        end_time = datetime.now(timezone.utc).isoformat()

        connection.execute("""
            UPDATE pipeline_runs
            SET end_time = ?,
                status = ?,
                input_count = ?,
                inserted_count = ?,
                skipped_count = ?,
                rejected_count = ?,
                error_message = ?
            WHERE run_id = ?
        """, (
            end_time,
            "FAILED",
            input_count,
            inserted_count,
            skipped_count,
            rejected_count,
            str(error),
            run_id
        ))

        connection.commit()

        print("Pipeline failed:", error)
        raise

    finally:
        connection.close()


if __name__ == "__main__":

    input_file = "data/input/customer_updates.csv"

    ingest_customer_data(input_file)
