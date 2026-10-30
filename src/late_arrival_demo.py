
from src.database import get_connection

connection = get_connection()

cursor = connection.cursor()

# Insert March event first
cursor.execute("""
    INSERT INTO customer_events
    (event_id, customer_id, customer_name, city,
     effective_date, source_file, run_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    "LATE003",
    "C300",
    "Sita",
    "Chennai",
    "2026-03-01",
    "late_test.csv",
    "LATE_RUN"
))

# Insert January event later
cursor.execute("""
    INSERT INTO customer_events
    (event_id, customer_id, customer_name, city,
     effective_date, source_file, run_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    "LATE001",
    "C300",
    "Sita",
    "Hyderabad",
    "2026-01-01",
    "late_test.csv",
    "LATE_RUN"
))

connection.commit()
connection.close()

print("Late-arriving test events inserted successfully!")
