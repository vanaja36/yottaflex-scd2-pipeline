
import pandas as pd
import random
import time
from pathlib import Path


def generate_customer_data(
    number_of_records=100_000,
    number_of_customers=10_000,
    seed=42
):

    start_time = time.time()

    # Fixed seed ensures reproducible data
    random.seed(seed)

    names = [
        "Ravi", "Priya", "Kumar", "Anjali",
        "Arjun", "Sneha", "Manoj", "Divya",
        "Kiran", "Meena"
    ]

    cities = [
        "Hyderabad", "Vijayawada", "Chennai",
        "Bangalore", "Mumbai", "Pune",
        "Delhi", "Kolkata"
    ]

    records = []

    for i in range(number_of_records):

        customer_number = random.randint(
            1, number_of_customers
        )

        customer_id = f"C{customer_number:06d}"

        customer_name = random.choice(names)
        city = random.choice(cities)

        # Generate dates between January and December 2026
        day_number = random.randint(1, 365)

        effective_date = (
            pd.Timestamp("2026-01-01")
            + pd.Timedelta(days=day_number - 1)
        ).strftime("%Y-%m-%d")

        event_id = f"EVT{i + 1:07d}"

        records.append({
            "customer_id": customer_id,
            "customer_name": customer_name,
            "city": city,
            "effective_date": effective_date,
            "event_id": event_id
        })

    df = pd.DataFrame(records)

    output_folder = Path("data/input")
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = output_folder / "large_customer_updates.csv"

    df.to_csv(output_file, index=False)

    end_time = time.time()

    print("\nDATA GENERATION SUMMARY")
    print("-----------------------")
    print("Total records:", len(df))
    print("Unique customers:", df["customer_id"].nunique())
    print("Random seed:", seed)
    print("Generation time:", round(end_time - start_time, 2), "seconds")
    print("Output file:", output_file)


if __name__ == "__main__":
    generate_customer_data()
