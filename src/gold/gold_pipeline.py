from pathlib import Path

import pandas as pd

from src.gold.gold_quality_report import (
    run_gold_quality_reports,
)

from src.gold.dim_event import (
    build_dim_event,
    save_dim_event,
    validate_dim_event,
)
from src.gold.dim_driver import (
    build_dim_driver,
    save_dim_driver,
    validate_dim_driver,
)
from src.gold.dim_team import (
    build_dim_team,
    save_dim_team,
    validate_dim_team,
)
from src.gold.fact_race_result import (
    build_fact_race_result,
    save_fact_race_result,
    validate_fact_race_result,
)

from src.gold.gold_validator import validate_star_schema

SILVER_EVENT_SCHEDULE_PATH = Path(
    "data/silver/event_schedule/event_schedule_2024.parquet"
)

SILVER_RACE_RESULTS_PATH = Path(
    "data/silver/race_results/race_results_2024.parquet"
)


def load_silver_datasets() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Loads the Silver datasets required by the Gold pipeline.
    """

    required_paths = [
        SILVER_EVENT_SCHEDULE_PATH,
        SILVER_RACE_RESULTS_PATH,
    ]

    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(
                f"Required Silver dataset not found: {path}"
            )

    silver_event_schedule = pd.read_parquet(
        SILVER_EVENT_SCHEDULE_PATH
    )

    silver_race_results = pd.read_parquet(
        SILVER_RACE_RESULTS_PATH
    )

    return (
        silver_event_schedule,
        silver_race_results,
    )


def run_gold_pipeline() -> None:
    """
    Executes the complete Gold transformation pipeline.

    Execution order:
        1. Load Silver datasets
        2. Build dimensions
        3. Validate dimensions
        4. Build fact table
        5. Validate fact table
        6. Persist Gold datasets
    """

    print("Starting Gold transformation pipeline.")

    (
        silver_event_schedule,
        silver_race_results,
    ) = load_silver_datasets()

    print("\n" + "=" * 80)
    print("Building dimension: dim_event")

    dim_event = build_dim_event(
        silver_event_schedule
    )

    validate_dim_event(dim_event)
    save_dim_event(dim_event)

    print("dim_event completed.")
    print(f"Rows: {len(dim_event)}")
    print(f"Columns: {len(dim_event.columns)}")

    print("\n" + "=" * 80)
    print("Building dimension: dim_driver")

    dim_driver = build_dim_driver(
        silver_race_results
    )

    validate_dim_driver(dim_driver)
    save_dim_driver(dim_driver)

    print("dim_driver completed.")
    print(f"Rows: {len(dim_driver)}")
    print(f"Columns: {len(dim_driver.columns)}")

    print("\n" + "=" * 80)
    print("Building dimension: dim_team")

    dim_team = build_dim_team(
        silver_race_results
    )

    validate_dim_team(dim_team)
    save_dim_team(dim_team)

    print("dim_team completed.")
    print(f"Rows: {len(dim_team)}")
    print(f"Columns: {len(dim_team.columns)}")

    print("\n" + "=" * 80)
    print("Building fact table: fact_race_result")

    fact_race_result = build_fact_race_result(
        silver_race_results=silver_race_results,
        dim_event=dim_event,
        dim_driver=dim_driver,
        dim_team=dim_team,
    )

    validate_fact_race_result(
        fact_race_result
    )

    save_fact_race_result(
        fact_race_result
    )

    print("fact_race_result completed.")
    print(f"Rows: {len(fact_race_result)}")
    print(
        f"Columns: {len(fact_race_result.columns)}"
    )

    print("\n" + "=" * 80)
    print("Validating complete Gold Star Schema")

    validate_star_schema(
        dim_event=dim_event,
        dim_driver=dim_driver,
        dim_team=dim_team,
        fact_race_result=fact_race_result,
    )

    print("\n" + "=" * 80)
    print("Generating Gold data quality reports")

    run_gold_quality_reports()

    print("\n" + "=" * 80)
    print(
        "Gold transformation pipeline completed successfully."
    )


def main() -> None:
    run_gold_pipeline()


if __name__ == "__main__":
    main()