from pathlib import Path

import pandas as pd

from src.transform.event_schedule import normalize_text_columns
from src.transform.schema import RACE_RESULTS_COLUMNS


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BRONZE_FILE = (
    PROJECT_ROOT
    / "data"
    / "bronze"
    / "race_results"
    / "race_results_2024.parquet"
)

SILVER_FILE = (
    PROJECT_ROOT
    / "data"
    / "silver"
    / "race_results"
    / "race_results_2024.parquet"
)


def load_bronze_race_results(
    file_path: Path,
) -> pd.DataFrame:
    """Load the race results dataset from the Bronze layer."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Bronze dataset not found: {file_path}"
        )

    return pd.read_parquet(file_path)


def validate_source_columns(
    dataframe: pd.DataFrame,
) -> None:
    """Validate whether all required source columns are available."""

    required_columns = set(RACE_RESULTS_COLUMNS)
    available_columns = set(dataframe.columns)

    missing_columns = required_columns - available_columns

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )


def convert_race_result_types(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Convert Race Results columns to their Silver data types."""

    transformed = dataframe.copy()

    integer_columns = [
        "season",
        "round_number",
        "driver_number",
        "grid_position",
        "finish_position",
        "laps",
    ]

    for column in integer_columns:
        transformed[column] = pd.to_numeric(
            transformed[column],
            errors="raise",
        ).astype("int64")

    transformed["points"] = pd.to_numeric(
        transformed["points"],
        errors="raise",
    ).astype("float64")

    return transformed


def transform_race_results(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Transform Bronze Race Results into the Silver format."""

    validate_source_columns(dataframe)

    transformed = dataframe[
        list(RACE_RESULTS_COLUMNS.keys())
    ].copy()

    transformed = transformed.rename(
        columns=RACE_RESULTS_COLUMNS
    )

    transformed = normalize_text_columns(transformed)

    transformed = convert_race_result_types(transformed)

    transformed = transformed.sort_values(
        by=[
            "season",
            "round_number",
            "finish_position",
        ]
    ).reset_index(drop=True)

    duplicated_keys = transformed[
        transformed.duplicated(
            subset=[
                "season",
                "round_number",
                "driver_number",
            ],
            keep=False,
        )
    ]

    if not duplicated_keys.empty:
        duplicated_records = duplicated_keys[
            [
                "season",
                "round_number",
                "driver_number",
            ]
        ]

        raise ValueError(
            "Duplicated Race Results business keys found.\n"
            f"{duplicated_records.to_string(index=False)}"
        )

    return transformed


def save_silver_race_results(
    dataframe: pd.DataFrame,
    file_path: Path,
) -> None:
    """Save transformed Race Results in the Silver layer."""

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_parquet(
        file_path,
        index=False,
    )


def main() -> None:
    """Run the Race Results Bronze-to-Silver transformation."""

    bronze_dataframe = load_bronze_race_results(
        BRONZE_FILE
    )

    silver_dataframe = transform_race_results(
        bronze_dataframe
    )

    save_silver_race_results(
        silver_dataframe,
        SILVER_FILE,
    )

    print("Race results transformation completed.")
    print(f"Bronze rows: {len(bronze_dataframe)}")
    print(f"Silver rows: {len(silver_dataframe)}")
    print(f"Silver columns: {len(silver_dataframe.columns)}")
    print(f"Output: {SILVER_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()