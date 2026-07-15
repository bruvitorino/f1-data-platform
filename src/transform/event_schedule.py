from pathlib import Path

import pandas as pd

from src.transform.schema import EVENT_SCHEDULE_COLUMNS


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BRONZE_FILE = (
    PROJECT_ROOT
    / "data"
    / "bronze"
    / "event_schedule_2024.parquet"
)

SILVER_FILE = (
    PROJECT_ROOT
    / "data"
    / "silver"
    / "event_schedule"
    / "event_schedule_2024.parquet"
)


def load_bronze_event_schedule(file_path: Path) -> pd.DataFrame:
    """Load the event schedule dataset from the Bronze layer."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Bronze dataset not found: {file_path}"
        )

    return pd.read_parquet(file_path)


def validate_source_columns(dataframe: pd.DataFrame) -> None:
    """Validate whether all required source columns are available."""

    required_columns = set(EVENT_SCHEDULE_COLUMNS)
    available_columns = set(dataframe.columns)

    missing_columns = required_columns - available_columns

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )


def normalize_text_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Strip unnecessary whitespace from text columns."""

    transformed = dataframe.copy()

    text_columns = transformed.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        transformed[column] = transformed[column].apply(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

    return transformed


def transform_event_schedule(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Transform the Bronze event schedule into the Silver format."""

    validate_source_columns(dataframe)

    transformed = dataframe[
        list(EVENT_SCHEDULE_COLUMNS.keys())
    ].copy()

    transformed = transformed.rename(
        columns=EVENT_SCHEDULE_COLUMNS
    )

    transformed = transformed[
        transformed["round_number"] > 0
    ].copy()

    transformed = normalize_text_columns(transformed)

    transformed = transformed.sort_values(
        by="round_number"
    ).reset_index(drop=True)

    duplicated_rounds = transformed[
        transformed.duplicated(
            subset=["round_number"],
            keep=False,
        )
    ]

    if not duplicated_rounds.empty:
        duplicate_values = (
            duplicated_rounds["round_number"]
            .unique()
            .tolist()
        )

        raise ValueError(
            f"Duplicated round numbers found: {duplicate_values}"
        )

    return transformed


def save_silver_event_schedule(
    dataframe: pd.DataFrame,
    file_path: Path,
) -> None:
    """Save the transformed event schedule in the Silver layer."""

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_parquet(
        file_path,
        index=False,
    )


def main() -> None:
    bronze_dataframe = load_bronze_event_schedule(
        BRONZE_FILE
    )

    silver_dataframe = transform_event_schedule(
        bronze_dataframe
    )

    save_silver_event_schedule(
        silver_dataframe,
        SILVER_FILE,
    )

    print("Event schedule transformation completed.")
    print(f"Bronze rows: {len(bronze_dataframe)}")
    print(f"Silver rows: {len(silver_dataframe)}")
    print(f"Silver columns: {len(silver_dataframe.columns)}")
    print(f"Output: {SILVER_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()