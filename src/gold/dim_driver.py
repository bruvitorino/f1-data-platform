from pathlib import Path

import pandas as pd

from src.gold.schema import DIM_DRIVER_COLUMNS


SILVER_RACE_RESULTS_PATH = Path(
    "data/silver/race_results/race_results_2024.parquet"
)

GOLD_DIM_DRIVER_PATH = Path(
    "data/gold/dimensions/dim_driver/dim_driver.parquet"
)


def build_dim_driver(
    silver_race_results: pd.DataFrame,
) -> pd.DataFrame:
    """
    Builds the driver dimension from Silver race results.

    Grain:
        One row per Formula 1 driver.

    Natural key:
        driver_id

    Surrogate key:
        driver_key
    """

    driver_columns = [
        "driver_id",
        "driver_number",
        "driver_abbreviation",
        "driver_name",
        "country_code",
    ]

    dim_driver = (
        silver_race_results[driver_columns]
        .drop_duplicates(subset=["driver_id"])
        .sort_values(by="driver_id")
        .reset_index(drop=True)
    )

    dim_driver["driver_key"] = dim_driver.index + 1

    dim_driver = dim_driver[DIM_DRIVER_COLUMNS]

    return dim_driver


def validate_dim_driver(
    dim_driver: pd.DataFrame,
) -> None:
    """
    Performs structural validations specific to dim_driver.
    """

    if dim_driver.empty:
        raise ValueError("dim_driver cannot be empty.")

    if dim_driver["driver_key"].isna().any():
        raise ValueError(
            "dim_driver contains null driver keys."
        )

    if dim_driver["driver_key"].duplicated().any():
        raise ValueError(
            "dim_driver contains duplicated driver keys."
        )

    if dim_driver["driver_id"].isna().any():
        raise ValueError(
            "dim_driver contains null driver IDs."
        )

    if dim_driver["driver_id"].duplicated().any():
        raise ValueError(
            "dim_driver contains duplicated driver IDs."
        )

    critical_columns = [
        "driver_key",
        "driver_id",
        "driver_name",
    ]

    if dim_driver[critical_columns].isna().any().any():
        raise ValueError(
            "dim_driver contains null values "
            "in critical columns."
        )


def save_dim_driver(
    dim_driver: pd.DataFrame,
) -> None:
    """
    Saves the driver dimension in the Gold layer.
    """

    GOLD_DIM_DRIVER_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dim_driver.to_parquet(
        GOLD_DIM_DRIVER_PATH,
        index=False,
    )


def main() -> None:
    print("Starting dim_driver build.")

    if not SILVER_RACE_RESULTS_PATH.exists():
        raise FileNotFoundError(
            "Silver Race Results dataset not found: "
            f"{SILVER_RACE_RESULTS_PATH}"
        )

    silver_race_results = pd.read_parquet(
        SILVER_RACE_RESULTS_PATH
    )

    dim_driver = build_dim_driver(
        silver_race_results
    )

    validate_dim_driver(dim_driver)

    save_dim_driver(dim_driver)

    print("dim_driver build completed.")
    print(f"Rows: {len(dim_driver)}")
    print(f"Columns: {len(dim_driver.columns)}")
    print(f"Output: {GOLD_DIM_DRIVER_PATH}")


if __name__ == "__main__":
    main()