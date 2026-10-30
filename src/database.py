
import sqlite3
from pathlib import Path


DB_PATH = Path("data/output/customer_database.db")


def get_connection():
    """Create a connection to the SQLite database."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    return connection


def create_tables():
    """Create source, dimension, and pipeline tracking tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # Source event table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_events (
            event_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            city TEXT NOT NULL,
            effective_date TEXT NOT NULL,
            source_file TEXT,
            run_id TEXT
        )
    """)

    # SCD Type 2 dimension table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_customer (
            customer_sk INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            city TEXT NOT NULL,
            effective_from TEXT NOT NULL,
            effective_to TEXT,
            is_current INTEGER NOT NULL,
            change_hash TEXT NOT NULL,
            UNIQUE(customer_id, effective_from)
        )
    """)

    # Pipeline execution tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id TEXT PRIMARY KEY,
            start_time TEXT NOT NULL,
            end_time TEXT,
            status TEXT NOT NULL,
            input_count INTEGER DEFAULT 0,
            inserted_count INTEGER DEFAULT 0,
            skipped_count INTEGER DEFAULT 0,
            rejected_count INTEGER DEFAULT 0,
            error_message TEXT
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_tables()
    print("Database and tables created successfully!")
