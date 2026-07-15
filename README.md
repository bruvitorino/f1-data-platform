# F1 Data Platform

An end-to-end Data Engineering project that collects, validates, transforms and models Formula 1 data using production-inspired engineering practices.

The project follows the Medallion Architecture and currently processes the 2024 Formula 1 season using data extracted from FastF1.

## Project Objectives

* Build a production-inspired Formula 1 data platform.
* Create reusable extraction and transformation pipelines.
* Apply the Medallion Architecture: Bronze, Silver and Gold.
* Implement automated data quality checks.
* Build an analytical Star Schema.
* Prepare data for dashboards and business analysis.
* Apply software engineering practices such as modularization, validation, documentation and version control.

## Current Architecture

```text
FastF1
   |
   v
Bronze Layer
├── event_schedule
└── race_results
   |
   v
Data Quality
   |
   v
Silver Layer
├── event_schedule
└── race_results
   |
   v
Silver Validation
   |
   v
Gold Layer
├── Dimensions
│   ├── dim_event
│   ├── dim_driver
│   └── dim_team
│
└── Facts
    └── fact_race_result
   |
   v
Gold Star Schema Validation
   |
   v
Automated Quality Reports
```

## Gold Star Schema

```text
                         dim_driver
                              |
                              |
dim_event -------- fact_race_result -------- dim_team
```

### Table Grain

| Table              | Grain                                  |
| ------------------ | -------------------------------------- |
| `dim_event`        | One row per Formula 1 event per season |
| `dim_driver`       | One row per driver                     |
| `dim_team`         | One row per team                       |
| `fact_race_result` | One row per driver per race            |

### Gold Dataset Results

| Dataset            | Rows | Columns |
| ------------------ | ---: | ------: |
| `dim_event`        |   24 |      20 |
| `dim_driver`       |   24 |       6 |
| `dim_team`         |   10 |       3 |
| `fact_race_result` |  479 |      18 |

## Data Quality and Validation

The project includes reusable and dataset-specific quality checks.

Current Gold validations include:

* Foreign key integrity.
* Fact table grain validation.
* Event coverage validation.
* Exactly one winner per race.
* Participant count analysis.
* Validation of nullable business fields.
* Detection of unused dimension records.
* Duplicate detection.
* Null value analysis.
* Empty column detection.
* Single-value column detection.
* Memory usage reporting.

Gold quality reports are generated automatically for:

```text
reports/gold/
├── dim_event_quality_report.txt
├── dim_driver_quality_report.txt
├── dim_team_quality_report.txt
└── fact_race_result_quality_report.txt
```

## Project Structure

```text
f1-data-platform/
├── assets/
├── configs/
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│       ├── dimensions/
│       └── facts/
├── docker/
├── docs/
├── reports/
│   └── gold/
├── src/
│   ├── extract/
│   ├── quality/
│   ├── transform/
│   └── gold/
├── tests/
├── README.md
└── requirements.txt
```

## Gold Modules

```text
src/gold/
├── dim_driver.py
├── dim_event.py
├── dim_team.py
├── fact_race_result.py
├── gold_pipeline.py
├── gold_quality_report.py
├── gold_validator.py
├── inspect_silver.py
├── schema.py
└── __init__.py
```

## Running the Pipelines

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Run the Silver transformation pipeline:

```powershell
python -m src.transform.transform_pipeline
```

Run the complete Gold pipeline:

```powershell
python -m src.gold.gold_pipeline
```

The Gold pipeline performs the following steps:

```text
Load Silver datasets
        |
        v
Build dimensions
        |
        v
Build fact table
        |
        v
Validate individual datasets
        |
        v
Validate complete Star Schema
        |
        v
Generate automated quality reports
```

## Technology Stack

### Current

* Python
* Pandas
* FastF1
* Parquet
* Git
* GitHub

### Planned

* PostgreSQL
* Apache Airflow
* Docker
* Power BI
* Automated tests
* CI/CD with GitHub Actions

## Sprint Progress

### Sprint 0 — Foundation

* Project structure.
* Python virtual environment.
* Git and GitHub setup.

### Sprint 1 — Bronze Event Schedule

* FastF1 integration.
* Event Schedule extraction.
* Parquet persistence.

### Sprint 2 — Data Quality Library

* Dataset analysis.
* Terminal report generation.
* Report persistence.

### Sprint 3 — Silver Event Schedule

* Bronze-to-Silver transformation.
* Schema contract.
* Silver validation.
* Transformation pipeline.

### Sprint 4 — Race Results

* Race Results extraction.
* Bronze-specific validation.
* Bronze quality report.
* Silver transformation.
* Schema contract.
* Silver pipeline integration.
* Automated Silver validation.

### Sprint 5 — Gold Layer and Star Schema

* Dimensional model design.
* `dim_event`.
* `dim_driver`.
* `dim_team`.
* `fact_race_result`.
* Surrogate keys.
* Referential integrity validation.
* Business rule validation.
* Automated Gold quality reports.
* Complete Gold transformation pipeline.

## Current Status

**Sprint 5 — Gold Layer and Star Schema completed.**

The next planned stage is the creation of analytical Data Marts for driver standings, team standings and performance statistics.
