from src.database import get_connection

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT COUNT(*)
    FROM customer_events
    WHERE event_id IN ('T001', 'T002')
""")

count = cursor.fetchone()[0]

print("Valid test records in database:", count)

cursor.execute("""
    SELECT customer_id, customer_name, city, event_id
    FROM customer_events
    WHERE event_id IN ('T001', 'T002')
""")

for row in cursor.fetchall():
    print(row)

connection.close()