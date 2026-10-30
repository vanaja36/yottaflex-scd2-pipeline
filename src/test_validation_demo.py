
import pandas as pd

from src.validation import validate_customer_data

# Create sample records for validation testing
data = [
    ["C101", "Ravi", "Hyderabad", "2026-01-01", "E101"],
    ["C102", "Priya", "Vijayawada", "2026-01-02", "E102"],
    ["C103", "Kumar", "", "2026-01-03", "E103"],
    ["", "Anjali", "Chennai", "2026-01-04", "E104"],
    ["C104", "Arjun", "Bangalore", "invalid-date", "E105"]
]

columns = [
    "customer_id",
    "customer_name",
    "city",
    "effective_date",
    "event_id"
]

df = pd.DataFrame(data, columns=columns)

# Validate records
valid_df, rejected_df = validate_customer_data(df)

# Create quarantine directory
import os
os.makedirs("data/rejected", exist_ok=True)

# Save rejected records
rejected_df.to_csv(
    "data/rejected/rejected_records.csv",
    index=False
)

# Display results
print("Total records:", len(df))
print("Valid records:", len(valid_df))
print("Rejected records:", len(rejected_df))

print("\nRejected record details:")
print(rejected_df[["customer_id", "rejection_reason"]])
