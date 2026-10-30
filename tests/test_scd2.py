
from src import database
from src.scd2 import apply_scd2


def prepare_test_database(monkeypatch, tmp_path):

    # Create a separate temporary database for testing
    test_db = tmp_path / "test_customer.db"

    monkeypatch.setattr(database, "DB_PATH", test_db)

    database.create_tables()

    return database.get_connection()


def insert_events(connection, events):

    connection.executemany("""
        INSERT INTO customer_events (
            event_id, customer_id, customer_name, city,
            effective_date, source_file, run_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, events)

    connection.commit()


def test_scd2_customer_history(monkeypatch, tmp_path):

    connection = prepare_test_database(monkeypatch, tmp_path)

    events = [
        ("TEST001", "C900", "Test User", "Hyderabad",
         "2026-01-01", "test.csv", "TEST_RUN"),

        ("TEST002", "C900", "Test User", "Bangalore",
         "2026-02-01", "test.csv", "TEST_RUN")
    ]

    insert_events(connection, events)
    connection.close()

    apply_scd2()

    connection = database.get_connection()

    rows = connection.execute("""
        SELECT city, effective_from, effective_to, is_current
        FROM dim_customer
        WHERE customer_id = 'C900'
        ORDER BY effective_from
    """).fetchall()

    connection.close()

    assert len(rows) == 2

    assert rows[0] == (
        "Hyderabad", "2026-01-01", "2026-02-01", 0
    )

    assert rows[1] == (
        "Bangalore", "2026-02-01", None, 1
    )


def test_same_date_updates(monkeypatch, tmp_path):

    connection = prepare_test_database(monkeypatch, tmp_path)

    events = [
        ("E001", "C901", "Test User", "Hyderabad",
         "2026-01-01", "test.csv", "TEST_RUN"),

        ("E002", "C901", "Test User", "Chennai",
         "2026-01-01", "test.csv", "TEST_RUN"),

        ("E003", "C901", "Test User", "Mumbai",
         "2026-02-01", "test.csv", "TEST_RUN")
    ]

    insert_events(connection, events)
    connection.close()

    apply_scd2()

    connection = database.get_connection()

    rows = connection.execute("""
        SELECT city, effective_from, effective_to, is_current
        FROM dim_customer
        WHERE customer_id = 'C901'
        ORDER BY effective_from
    """).fetchall()

    connection.close()

    assert len(rows) == 2

    # E002 wins because it has the highest event_id
    assert rows[0] == (
        "Chennai", "2026-01-01", "2026-02-01", 0
    )

    assert rows[1] == (
        "Mumbai", "2026-02-01", None, 1
    )


def test_unchanged_customer_details(monkeypatch, tmp_path):

    connection = prepare_test_database(monkeypatch, tmp_path)

    events = [
        ("E101", "C902", "Ravi", "Hyderabad",
         "2026-01-01", "test.csv", "TEST_RUN"),

        ("E102", "C902", "Ravi", "Hyderabad",
         "2026-02-01", "test.csv", "TEST_RUN"),

        ("E103", "C902", "Ravi", "Hyderabad",
         "2026-03-01", "test.csv", "TEST_RUN")
    ]

    insert_events(connection, events)
    connection.close()

    apply_scd2()

    connection = database.get_connection()

    rows = connection.execute("""
        SELECT customer_name, city, effective_from,
               effective_to, is_current
        FROM dim_customer
        WHERE customer_id = 'C902'
    """).fetchall()

    connection.close()

    # Unchanged details should create only one version
    assert len(rows) == 1

    assert rows[0] == (
        "Ravi", "Hyderabad", "2026-01-01", None, 1
    )



def test_late_arriving_event(monkeypatch, tmp_path):

    connection = prepare_test_database(monkeypatch, tmp_path)

    events = [
        # Newer event arrives first
        ("E203", "C903", "Sita", "Chennai",
         "2026-03-01", "test.csv", "TEST_RUN"),

        # Older event arrives later
        ("E201", "C903", "Sita", "Hyderabad",
         "2026-01-01", "test.csv", "TEST_RUN"),

        ("E202", "C903", "Sita", "Bangalore",
         "2026-02-01", "test.csv", "TEST_RUN")
    ]

    insert_events(connection, events)
    connection.close()

    apply_scd2()

    connection = database.get_connection()

    rows = connection.execute("""
        SELECT city, effective_from, effective_to, is_current
        FROM dim_customer
        WHERE customer_id = 'C903'
        ORDER BY effective_from
    """).fetchall()

    connection.close()

    assert len(rows) == 3

    assert rows[0] == (
        "Hyderabad", "2026-01-01", "2026-02-01", 0
    )

    assert rows[1] == (
        "Bangalore", "2026-02-01", "2026-03-01", 0
    )

    assert rows[2] == (
        "Chennai", "2026-03-01", None, 1
    )
