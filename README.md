
# Customer Data Pipeline with SCD Type 2

## 1. Project Overview

This project implements an end-to-end customer data pipeline using Python, Pandas, and SQLite.

The pipeline ingests customer update records from CSV files, validates data quality, stores source events, and maintains historical customer records using Slowly Changing Dimension Type 2 (SCD Type 2).

It supports duplicate detection, invalid-record rejection, late-arriving data, idempotent transformations, reconciliation, and performance benchmarking.

## 2. Architecture

```text
             Customer CSV Files
                     |
                     v
              Data Ingestion
                     |
                     v
              Data Validation
                /        \
               /          \
              v            v
       Valid Records   Rejected Records
              |            |
              v            v
       SQLite Source    Rejected CSV
       Event Table
              |
              v
       SCD Type 2 Processing
              |
              v
       Customer Dimension
              |
              v
       Data Quality Checks
              |
              v
       Reconciliation Report
```

## 3. Technology Stack

- Python
- Pandas
- SQLite
- Pytest
- CSV
- Git and GitHub

## 4. Project Structure

```text
yottaflex_scd2_pipeline/
|
|-- data/
|   |-- input/
|   |-- output/
|   |-- rejected/
|
|-- src/
|   |-- database.py
|   |-- ingestion.py
|   |-- validation.py
|   |-- scd2.py
|   |-- reconciliation.py
|   |-- generate_data.py
|   |-- benchmark_ingestion.py
|   |-- benchmark_scd2.py
|   |-- verify_scd2.py
|   |-- test_idempotency.py
|
|-- tests/
|   |-- test_validation.py
|   |-- test_scd2.py
|
|-- reports/
|   |-- reconciliation_report.csv
|
|-- main.py
|-- requirements.txt
|-- README.md
```

## 5. SCD Type 2 Implementation

The customer dimension maintains historical versions of customer information.

Important columns:

| Column | Description |
|---|---|
| customer_sk | Surrogate primary key |
| customer_id | Business customer identifier |
| customer_name | Customer name |
| city | Customer city |
| effective_from | Start date of the version |
| effective_to | End date of the version |
| is_current | Indicates the current version |
| change_hash | Hash used for change detection |

### Business Rules

1. A new customer creates an initial dimension record.
2. A change in customer name or city creates a new version.
3. The previous version is closed using the new version's effective date.
4. The current version has `is_current = 1` and a NULL `effective_to`.
5. Unchanged customer attributes do not create unnecessary versions.
6. Late-arriving events are handled by rebuilding customer history in effective-date order.
7. For multiple events on the same customer and effective date, the highest event_id is selected as a deterministic tie-breaker.

Note: The same-date tie-breaker is an assumption because the source data does not provide a separate event timestamp or sequence.

## 6. Data Validation

The pipeline validates:

- Required columns.
- Missing customer identifiers.
- Missing customer names and cities.
- Invalid effective dates.
- Duplicate event IDs within a batch.

Invalid records are written to a rejected-record CSV file with rejection reasons.

Existing event IDs are skipped during ingestion to support idempotent loading.

## 7. Installation

Clone the repository:

git clone https://github.com/vanaja36/yottaflex-scd2-pipeline.git
cd yottaflex-scd2-pipeline

python -m pip install -r requirements.txt

Install dependencies:

```bash
pip install -r requirements.txt
```

## 8. Run the Pipeline

Create database tables:

```bash
python -m src.database
```

Run ingestion:

```bash
python -m src.ingestion
```

Apply SCD Type 2:

```bash
python -m src.scd2
```

Generate reconciliation report:

```bash
python -m src.reconciliation
```

## 9. Generate Large Test Data

Generate 100,000 customer update records:

```bash
python -m src.generate_data
```

This generator uses a fixed random seed for reproducible test data.

## 10. Performance Benchmarking

Run ingestion benchmark:

```bash
python -m src.benchmark_ingestion
```

Run SCD Type 2 benchmark:

```bash
python -m src.benchmark_scd2
```

### Recorded Benchmark Results

| Metric | Result |
|---|---:|
| Input events | 100,000 |
| Unique customers | 10,000 |
| Unique customer-date events | 98,597 |
| Dimension versions | 97,511 |
| Current customer versions | 10,000 |
| SCD2 execution time | 0.77 seconds |
| Processing speed | 130,618 events/second |

Benchmark results depend on the execution environment.

## 11. Data Quality Verification

Run:

```bash
python -m src.verify_scd2
```

The verification checks:

- Exactly one current record per customer.
- No duplicate customer effective dates.
- No invalid effective date ranges.
- No current records with an end date.

All four checks passed during the recorded benchmark.

## 12. Automated Testing

Run the complete test suite:

```bash
python -m pytest -v
```

### Test Results

**11 automated tests passed.**

Coverage includes:

- Valid and invalid records.
- Empty input.
- Duplicate event IDs.
- Missing required columns.
- Missing customer IDs.
- Invalid date formats.
- SCD Type 2 customer history.
- Same-date updates.
- Unchanged customer details.
- Late-arriving events.
- Idempotency.

## 13. Reconciliation and Observability

The pipeline tracks:

- Run ID.
- Start and end time.
- Pipeline status.
- Input record count.
- Inserted record count.
- Skipped duplicate count.
- Rejected record count.
- Error messages.

The reconciliation report compares input records against inserted, skipped, and rejected records.

## 14. Limitations and Future Improvements

- Add source event timestamps or sequence numbers for accurate same-day event ordering.
- Improve incremental SCD Type 2 processing instead of rebuilding complete customer timelines.
- Add schema evolution handling.
- Add automated retry and recovery for partial failures.
- Add cloud deployment and orchestration.
- Improve large-scale ingestion using chunked processing.

## 15. Author
## Author

Vanaja Pandella

GitHub: https://github.com/vanaja36
Developed as a data engineering challenge project.

**Project:** Customer Data Pipeline with SCD Type 2
