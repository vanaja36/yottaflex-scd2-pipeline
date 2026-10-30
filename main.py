
from src.database import create_tables
from src.ingestion import ingest_customer_data
from src.scd2 import apply_scd2
from src.reconciliation import generate_reconciliation_report


def run_pipeline():

    input_file = "data/input/customer_updates.csv"

    print("\n================================")
    print("CUSTOMER DATA PIPELINE STARTED")
    print("================================")

    # Step 1: Create database tables
    print("\nStep 1: Creating database tables...")
    create_tables()

    # Step 2: Ingest customer records
    print("\nStep 2: Ingesting customer data...")
    ingest_customer_data(input_file)

    # Step 3: Apply SCD Type 2
    print("\nStep 3: Applying SCD Type 2...")
    apply_scd2()

    # Step 4: Generate reconciliation report
    print("\nStep 4: Generating reconciliation report...")
    generate_reconciliation_report()

    print("\n================================")
    print("CUSTOMER DATA PIPELINE COMPLETED")
    print("================================")


if __name__ == "__main__":
    run_pipeline()
