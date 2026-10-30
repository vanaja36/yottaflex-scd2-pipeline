
import sqlite3

DB_PATH = "data/output/benchmark_database.db"

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

checks = {
    "Customers without exactly one current record": """
        SELECT COUNT(*)
        FROM (
            SELECT customer_id
            FROM dim_customer
            GROUP BY customer_id
            HAVING SUM(is_current) != 1
        )
    """,

    "Duplicate customer effective dates": """
        SELECT COUNT(*)
        FROM (
            SELECT customer_id, effective_from
            FROM dim_customer
            GROUP BY customer_id, effective_from
            HAVING COUNT(*) > 1
        )
    """,

    "Invalid date ranges": """
        SELECT COUNT(*)
        FROM dim_customer
        WHERE effective_to IS NOT NULL
          AND effective_to <= effective_from
    """,

    "Current records with an end date": """
        SELECT COUNT(*)
        FROM dim_customer
        WHERE is_current = 1
          AND effective_to IS NOT NULL
    """
}

print("\nSCD TYPE 2 DATA QUALITY CHECKS")
print("------------------------------")

for check_name, query in checks.items():

    cursor.execute(query)
    result = cursor.fetchone()[0]

    print(f"{check_name}: {result}")

connection.close()
