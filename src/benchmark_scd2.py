
import sqlite3
import time
from pathlib import Path

from src import database
from src.scd2 import apply_scd2


def run_scd2_benchmark():

    # Use the separate benchmark database
    benchmark_db = Path("data/output/benchmark_database.db")

    original_db_path = database.DB_PATH

    try:
        database.DB_PATH = benchmark_db

        # Check source record count
        connection = sqlite3.connect(benchmark_db)

        source_count = connection.execute(
            "SELECT COUNT(*) FROM customer_events"
        ).fetchone()[0]

        customer_count = connection.execute(
            "SELECT COUNT(DISTINCT customer_id) FROM customer_events"
        ).fetchone()[0]

        connection.close()

        print("Starting SCD Type 2 benchmark...")
        print("Source events:", source_count)
        print("Unique customers:", customer_count)

        # Measure transformation time
        start_time = time.perf_counter()

        apply_scd2()

        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        # Read dimension table metrics
        connection = sqlite3.connect(benchmark_db)

        dimension_count = connection.execute(
            "SELECT COUNT(*) FROM dim_customer"
        ).fetchone()[0]

        current_count = connection.execute(
            "SELECT COUNT(*) FROM dim_customer WHERE is_current = 1"
        ).fetchone()[0]

        connection.close()

        records_per_second = (
            source_count / elapsed_time
            if elapsed_time > 0 else 0
        )

        print("\nSCD TYPE 2 PERFORMANCE REPORT")
        print("-----------------------------")
        print("Source events:", source_count)
        print("Customers:", customer_count)
        print("Dimension versions:", dimension_count)
        print("Current customer versions:", current_count)
        print("Execution time:", round(elapsed_time, 2), "seconds")
        print("Source events processed per second:", round(records_per_second, 2))

        print("\nBenchmark database:", benchmark_db)

    finally:
        database.DB_PATH = original_db_path


if __name__ == "__main__":
    run_scd2_benchmark()
