
import hashlib
from src.database import get_connection


def generate_hash(customer_name, city):
    """
    Generate a hash using customer attributes.
    This helps identify whether customer details changed.
    """
    value = f"{customer_name}|{city}"
    return hashlib.sha256(value.encode()).hexdigest()


def apply_scd2():

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Step 1: Read all source events in date order
        cursor.execute("""
            SELECT
                customer_id,
                customer_name,
                city,
                effective_date,
                event_id
            FROM customer_events
            ORDER BY customer_id, effective_date, event_id
        """)

        source_events = cursor.fetchall()

        # Step 2: Keep one event per customer per effective date.
        # If multiple events exist on the same date,
        # the highest event_id is selected.
        daily_events = {}

        for event in source_events:

            customer_id, name, city, effective_date, event_id = event

            key = (customer_id, effective_date)

            if (
                key not in daily_events
                or event_id > daily_events[key][4]
            ):
                daily_events[key] = event

        events = list(daily_events.values())

        events.sort(
            key=lambda event: (
                event[0],
                event[3],
                event[4]
            )
        )

        # Step 3: Group events by customer
        customers = {}

        for event in events:

            customer_id, name, city, effective_date, event_id = event

            customers.setdefault(customer_id, []).append(
                (name, city, effective_date, event_id)
            )

        # Step 4: Rebuild each customer's timeline
        for customer_id, customer_events in customers.items():

            cursor.execute(
                "DELETE FROM dim_customer WHERE customer_id = ?",
                (customer_id,)
            )

            previous_hash = None
            history = []

            for name, city, effective_date, event_id in customer_events:

                current_hash = generate_hash(name, city)

                # Skip unchanged customer details
                if current_hash == previous_hash:
                    continue

                # Close the previous version
                if history:
                    history[-1]["effective_to"] = effective_date
                    history[-1]["is_current"] = 0

                # Create a new version
                history.append({
                    "customer_id": customer_id,
                    "customer_name": name,
                    "city": city,
                    "effective_from": effective_date,
                    "effective_to": None,
                    "is_current": 1,
                    "change_hash": current_hash
                })

                previous_hash = current_hash

            # Step 5: Insert history into dimension table
            for record in history:

                cursor.execute("""
                    INSERT INTO dim_customer (
                        customer_id,
                        customer_name,
                        city,
                        effective_from,
                        effective_to,
                        is_current,
                        change_hash
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    record["customer_id"],
                    record["customer_name"],
                    record["city"],
                    record["effective_from"],
                    record["effective_to"],
                    record["is_current"],
                    record["change_hash"]
                ))

        connection.commit()

        print("SCD Type 2 transformation completed!")
        print("Source events processed:", len(source_events))
        print("Unique customer-date events:", len(events))
        print("Customers processed:", len(customers))

        cursor.execute("SELECT COUNT(*) FROM dim_customer")
        print("Dimension records created:", cursor.fetchone()[0])

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    apply_scd2()
