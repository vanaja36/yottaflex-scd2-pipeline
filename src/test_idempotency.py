
import sqlite3
import hashlib

from pathlib import Path
from src import database
from src.scd2 import apply_scd2


def get_dimension_snapshot(db_path):

    connection = sqlite3.connect(db_path)

    rows = connection.execute("""
        SELECT
            customer_id,
            customer_name,
            city,
            effective_from,
            effective_to,
            is_current,
            change_hash
        FROM dim_customer
        ORDER BY customer_id, effective_from
    """).fetchall()

    connection.close()

    return hashlib.sha256(
        repr(rows).encode("utf-8")
    ).hexdigest(), len(rows)


def test_idempotency():

    benchmark_db = Path("data/output/benchmark_database.db")

    original_db_path = database.DB_PATH

    try:
        database.DB_PATH = benchmark_db

        # Capture dimension state before rerunning
        before_hash, before_count = get_dimension_snapshot(
            benchmark_db
        )

        print("Dimension records before rerun:", before_count)

        # Run SCD Type 2 transformation again
        print("\nRunning SCD Type 2 transformation again...")
        apply_scd2()

        # Capture dimension state after rerunning
        after_hash, after_count = get_dimension_snapshot(
            benchmark_db
        )

        print("\nDimension records after rerun:", after_count)

        if before_hash == after_hash:
            print("\nIDEMPOTENCY TEST: PASSED")
            print("Dimension data remained unchanged.")
        else:
            print("\nIDEMPOTENCY TEST: FAILED")
            print("Dimension data changed after rerun.")

    finally:
        database.DB_PATH = original_db_path


if __name__ == "__main__":
    test_idempotency()
