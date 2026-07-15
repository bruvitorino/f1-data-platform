from pathlib import Path

import pandas as pd

from src.gold.schema import DIM_EVENT_COLUMNS


SILVER_EVENT_SCHEDULE_PATH = Path(
    "data/silver/event_schedule/event_schedule_2024.parquet"
)

GOLD_DIM_EVENT_PATH = Path(
    "data/gold/dimensions/dim_event/dim_event_2024.parquet"
)


def build_dim_event(
    silver_event_schedule: pd.DataFrame,
) -> pd.DataFrame:
    """
    Builds the event dimension from the Silver event schedule.

    Grain:
        One row per Formula 1 event in a season.

    Natural key:
        season + round_number

    Surrogate key:
        event_key
    """

    dim_event = silver_event_schedule.copy()

    dim_event["season"] = dim_event["event_date"].dt.year

    dim_event = dim_event.sort_values(
        by=["season", "round_number"]
    ).reset_index(drop=True)

    dim_event["event_key"] = dim_event.index + 1

    dim_event = dim_event[DIM_EVENT_COLUMNS]

    return dim_event


def validate_dim_event(dim_event: pd.DataFrame) -> None:
    """
    Performs structural validations specific to dim_event.
    """

    if dim_event.empty:
        raise ValueError("dim_event cannot be empty.")

    if dim_event["event_key"].isna().any():
        raise ValueError("dim_event contains null event keys.")

    if dim_event["event_key"].duplicated().any():
        raise ValueError("dim_event contains duplicated event keys.")

    natural_key_columns = [
        "season",
        "round_number",
    ]

    if dim_event.duplicated(
        subset=natural_key_columns
    ).any():
        raise ValueError(
            "dim_event contains duplicated natural keys: "
            "season + round_number."
        )

    critical_columns = [
        "event_key",
        "season",
        "round_number",
        "event_name",
        "event_date",
    ]

    if dim_event[critical_columns].isna().any().any():
        raise ValueError(
            "dim_event contains null values in critical columns."
        )


def save_dim_event(dim_event: pd.DataFrame) -> None:
    """
    Saves the event dimension in the Gold layer.
    """

    GOLD_DIM_EVENT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dim_event.to_parquet(
        GOLD_DIM_EVENT_PATH,
        index=False,
    )


def main() -> None:
    print("Starting dim_event build.")

    if not SILVER_EVENT_SCHEDULE_PATH.exists():
        raise FileNotFoundError(
            "Silver Event Schedule dataset not found: "
            f"{SILVER_EVENT_SCHEDULE_PATH}"
        )

    silver_event_schedule = pd.read_parquet(
        SILVER_EVENT_SCHEDULE_PATH
    )

    dim_event = build_dim_event(
        silver_event_schedule
    )

    validate_dim_event(dim_event)

    save_dim_event(dim_event)

    print("dim_event build completed.")
    print(f"Rows: {len(dim_event)}")
    print(f"Columns: {len(dim_event.columns)}")
    print(f"Output: {GOLD_DIM_EVENT_PATH}")


if __name__ == "__main__":
    main()