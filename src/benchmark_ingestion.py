
import sqlite3
import time
import uuid
from pathlib import Path

from src.ingestion import ingest_customer_data


def run_ingestion_benchmark():

    # Create a separate benchmark database
    benchmark_db = Path("data/output/benchmark_database.db")
    benchmark_db.parent.mkdir(parents=True, exist_ok=True)

    # Save the original database path
    from src import database

    original_db_path = database.DB_PATH

    try:
        # Temporarily use the benchmark database
        database.DB_PATH = benchmark_db

        # Create the required tables
        database.create_tables()

        input_file = "data/input/large_customer_updates.csv"

        print("Starting 100,000-record ingestion benchmark...")

        start_time = time.perf_counter()

        # Run the existing ingestion pipeline
        ingest_customer_data(input_file)

        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        # Read benchmark results
        connection = sqlite3.connect(benchmark_db)

        result = connection.execute("""
            SELECT
                input_count,
                inserted_count,
                skipped_count,
                rejected_count,
                status
            FROM pipeline_runs
            ORDER BY start_time DESC
            LIMIT 1
        """).fetchone()

        connection.close()

        input_count, inserted, skipped, rejected, status = result

        records_per_second = (
            inserted / elapsed_time if elapsed_time > 0 else 0
        )

        print("\nINGESTION PERFORMANCE REPORT")
        print("----------------------------")
        print("Input records:", input_count)
        print("Inserted records:", inserted)
        print("Skipped records:", skipped)
        print("Rejected records:", rejected)
        print("Pipeline status:", status)
        print("Execution time:", round(elapsed_time, 2), "seconds")
        print("Inserted records per second:", round(records_per_second, 2))

        print("\nBenchmark database:", benchmark_db)

    finally:
        # Restore original database path
        database.DB_PATH = original_db_path


if __name__ == "__main__":
    run_ingestion_benchmark()
