from pathlib import Path

import pandas as pd


GOLD_DIM_EVENT_PATH = Path(
    "data/gold/dimensions/dim_event/dim_event_2024.parquet"
)

GOLD_DIM_DRIVER_PATH = Path(
    "data/gold/dimensions/dim_driver/dim_driver.parquet"
)

GOLD_DIM_TEAM_PATH = Path(
    "data/gold/dimensions/dim_team/dim_team.parquet"
)

GOLD_FACT_RACE_RESULT_PATH = Path(
    "data/gold/facts/fact_race_result/"
    "fact_race_result_2024.parquet"
)


def validate_foreign_key(
    fact: pd.DataFrame,
    dimension: pd.DataFrame,
    key_column: str,
    dimension_name: str,
) -> None:
    """
    Validates that every foreign key used in the fact table
    exists in its corresponding dimension.
    """

    fact_keys = set(
        fact[key_column].dropna().unique()
    )

    dimension_keys = set(
        dimension[key_column].dropna().unique()
    )

    orphan_keys = fact_keys - dimension_keys

    if orphan_keys:
        raise ValueError(
            f"Foreign key validation failed for "
            f"{dimension_name}. "
            f"Orphan keys found: {sorted(orphan_keys)}"
        )


def validate_unused_dimension_records(
    fact: pd.DataFrame,
    dimension: pd.DataFrame,
    key_column: str,
    dimension_name: str,
) -> list:
    """
    Identifies dimension records that are not referenced
    by the fact table.

    Unused dimension records are reported as warnings,
    because they are not necessarily data quality errors.
    """

    fact_keys = set(
        fact[key_column].dropna().unique()
    )

    dimension_keys = set(
        dimension[key_column].dropna().unique()
    )

    return sorted(dimension_keys - fact_keys)


def validate_star_schema(
    dim_event: pd.DataFrame,
    dim_driver: pd.DataFrame,
    dim_team: pd.DataFrame,
    fact_race_result: pd.DataFrame,
) -> None:
    """
    Validates the complete Gold Star Schema.
    """

    print("Starting Gold Star Schema validation.")

    print("\n" + "=" * 80)
    print("Validating foreign keys")

    validate_foreign_key(
        fact=fact_race_result,
        dimension=dim_event,
        key_column="event_key",
        dimension_name="dim_event",
    )

    validate_foreign_key(
        fact=fact_race_result,
        dimension=dim_driver,
        key_column="driver_key",
        dimension_name="dim_driver",
    )

    validate_foreign_key(
        fact=fact_race_result,
        dimension=dim_team,
        key_column="team_key",
        dimension_name="dim_team",
    )

    print("Foreign key validation passed.")

    print("\n" + "=" * 80)
    print("Validating fact table grain")

    duplicated_grain = fact_race_result.duplicated(
        subset=[
            "event_key",
            "driver_key",
        ]
    )

    if duplicated_grain.any():
        raise ValueError(
            "fact_race_result violates its declared grain."
        )

    print(
        "Fact grain validation passed: "
        "one row per driver per event."
    )

    print("\n" + "=" * 80)
    print("Validating event coverage")

    fact_event_count = (
        fact_race_result["event_key"].nunique()
    )

    dimension_event_count = (
        dim_event["event_key"].nunique()
    )

    if fact_event_count != dimension_event_count:
        raise ValueError(
            "Event coverage mismatch. "
            f"dim_event contains {dimension_event_count} events, "
            f"but fact_race_result contains "
            f"{fact_event_count} events."
        )

    print(
        f"Event coverage validation passed: "
        f"{fact_event_count} events."
    )

    print("\n" + "=" * 80)
    print("Validating winners")

    winners_per_event = (
        fact_race_result
        .groupby("event_key")["is_winner"]
        .sum()
    )

    invalid_winner_events = winners_per_event[
        winners_per_event != 1
    ]

    if not invalid_winner_events.empty:
        raise ValueError(
            "Some events do not have exactly one winner. "
            f"Invalid events: "
            f"{invalid_winner_events.to_dict()}"
        )

    print("Winner validation passed.")

    print("\n" + "=" * 80)
    print("Validating participant counts")

    participants_per_event = (
        fact_race_result
        .groupby("event_key")
        .size()
    )

    if (participants_per_event <= 0).any():
        raise ValueError(
            "At least one event has no participants."
        )

    print("Participants per event:")
    print(
        participants_per_event.describe().to_string()
    )

    print("\n" + "=" * 80)
    print("Validating nullable business fields")

    classified_numeric_nulls = fact_race_result[
        "classified_position_numeric"
    ].isna()

    classified_original_is_numeric = pd.to_numeric(
        fact_race_result["classified_position"],
        errors="coerce",
    ).notna()

    invalid_classified_nulls = (
        classified_numeric_nulls
        & classified_original_is_numeric
    )

    if invalid_classified_nulls.any():
        raise ValueError(
            "classified_position_numeric contains nulls "
            "for numeric classified positions."
        )

    race_time_nulls = fact_race_result[
        "race_time_or_gap"
    ].isna()

    race_time_ms_nulls = fact_race_result[
        "race_time_or_gap_ms"
    ].isna()

    if not race_time_nulls.equals(
        race_time_ms_nulls
    ):
        raise ValueError(
            "race_time_or_gap and race_time_or_gap_ms "
            "have inconsistent null patterns."
        )

    positions_gained_nulls = fact_race_result[
        "positions_gained"
    ].isna()

    invalid_positions_gained_nulls = (
        positions_gained_nulls
        & fact_race_result["grid_position"].ne(0)
    )

    if invalid_positions_gained_nulls.any():
        raise ValueError(
            "positions_gained contains unexpected nulls."
        )

    expected_positions_gained_nulls = (
        fact_race_result["grid_position"].eq(0)
    )

    if not positions_gained_nulls.equals(
        expected_positions_gained_nulls
    ):
        raise ValueError(
            "positions_gained null pattern does not match "
            "grid_position equal to zero."
        )

    print(
        "Nullable business fields validation passed."
    )

    print("\n" + "=" * 80)
    print("Checking unused dimension records")

    dimensions = [
        (
            dim_event,
            "event_key",
            "dim_event",
        ),
        (
            dim_driver,
            "driver_key",
            "dim_driver",
        ),
        (
            dim_team,
            "team_key",
            "dim_team",
        ),
    ]

    for dimension, key_column, name in dimensions:
        unused_keys = validate_unused_dimension_records(
            fact=fact_race_result,
            dimension=dimension,
            key_column=key_column,
            dimension_name=name,
        )

        if unused_keys:
            print(
                f"WARNING: {name} contains unused keys: "
                f"{unused_keys}"
            )
        else:
            print(
                f"{name}: all records are referenced."
            )

    print("\n" + "=" * 80)
    print(
        "Gold Star Schema validation completed successfully."
    )


def load_gold_datasets() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """
    Loads all Gold datasets required for validation.
    """

    required_paths = [
        GOLD_DIM_EVENT_PATH,
        GOLD_DIM_DRIVER_PATH,
        GOLD_DIM_TEAM_PATH,
        GOLD_FACT_RACE_RESULT_PATH,
    ]

    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(
                f"Required Gold dataset not found: {path}"
            )

    dim_event = pd.read_parquet(
        GOLD_DIM_EVENT_PATH
    )

    dim_driver = pd.read_parquet(
        GOLD_DIM_DRIVER_PATH
    )

    dim_team = pd.read_parquet(
        GOLD_DIM_TEAM_PATH
    )

    fact_race_result = pd.read_parquet(
        GOLD_FACT_RACE_RESULT_PATH
    )

    return (
        dim_event,
        dim_driver,
        dim_team,
        fact_race_result,
    )


def main() -> None:
    (
        dim_event,
        dim_driver,
        dim_team,
        fact_race_result,
    ) = load_gold_datasets()

    validate_star_schema(
        dim_event=dim_event,
        dim_driver=dim_driver,
        dim_team=dim_team,
        fact_race_result=fact_race_result,
    )


if __name__ == "__main__":
    main()
