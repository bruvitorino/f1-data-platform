from pathlib import Path

import pandas as pd

from src.gold.schema import FACT_RACE_RESULT_COLUMNS


SILVER_RACE_RESULTS_PATH = Path(
    "data/silver/race_results/race_results_2024.parquet"
)

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


def build_fact_race_result(
    silver_race_results: pd.DataFrame,
    dim_event: pd.DataFrame,
    dim_driver: pd.DataFrame,
    dim_team: pd.DataFrame,
) -> pd.DataFrame:
    """
    Builds the race result fact table.

    Grain:
        One row per driver per Formula 1 race.

    Natural key:
        season + round_number + driver_id
    """

    fact = silver_race_results.copy()

    event_lookup = dim_event[
        [
            "event_key",
            "season",
            "round_number",
        ]
    ]

    driver_lookup = dim_driver[
        [
            "driver_key",
            "driver_id",
        ]
    ]

    team_lookup = dim_team[
        [
            "team_key",
            "team_id",
        ]
    ]

    fact = fact.merge(
        event_lookup,
        on=["season", "round_number"],
        how="left",
        validate="many_to_one",
    )

    fact = fact.merge(
        driver_lookup,
        on="driver_id",
        how="left",
        validate="many_to_one",
    )

    fact = fact.merge(
        team_lookup,
        on="team_id",
        how="left",
        validate="many_to_one",
    )

    fact["classified_position_numeric"] = pd.to_numeric(
        fact["classified_position"],
        errors="coerce",
    ).astype("Int64")

    fact["race_time_or_gap"] = fact["race_time"]

    fact["race_time_or_gap_ms"] = (
        fact["race_time"]
        .dt.total_seconds()
        .mul(1000)
        .round()
        .astype("Int64")
    )

    fact["positions_gained"] = (
        fact["grid_position"]
        - fact["finish_position"]
    ).astype("Int64")

    fact.loc[
        fact["grid_position"] == 0,
        "positions_gained",
    ] = pd.NA

    fact["is_winner"] = (
        fact["finish_position"] == 1
    )

    fact["is_podium"] = (
        fact["finish_position"].between(1, 3)
    )

    fact["is_points_finish"] = (
        fact["points"] > 0
    )

    classified_status = (
        fact["status"].eq("Finished")
        | fact["status"].str.match(
            r"^\+\d+ Laps?$",
            na=False,
        )
    )

    fact["is_dnf"] = ~classified_status

    fact = fact.sort_values(
        by=[
            "season",
            "round_number",
            "finish_position",
            "driver_id",
        ]
    ).reset_index(drop=True)

    fact["race_result_key"] = fact.index + 1

    fact = fact[FACT_RACE_RESULT_COLUMNS]

    return fact


def validate_fact_race_result(
    fact_race_result: pd.DataFrame,
) -> None:
    """
    Performs structural and referential validations
    for fact_race_result.
    """

    if fact_race_result.empty:
        raise ValueError(
            "fact_race_result cannot be empty."
        )

    key_columns = [
        "race_result_key",
        "event_key",
        "driver_key",
        "team_key",
    ]

    if fact_race_result[key_columns].isna().any().any():
        raise ValueError(
            "fact_race_result contains null keys."
        )

    if fact_race_result[
        "race_result_key"
    ].duplicated().any():
        raise ValueError(
            "fact_race_result contains duplicated "
            "race_result keys."
        )

    grain_columns = [
        "event_key",
        "driver_key",
    ]

    if fact_race_result.duplicated(
        subset=grain_columns
    ).any():
        raise ValueError(
            "fact_race_result violates its grain: "
            "one row per driver per event."
        )

    metric_columns = [
        "grid_position",
        "finish_position",
        "points",
        "laps",
    ]

    if fact_race_result[
        metric_columns
    ].isna().any().any():
        raise ValueError(
            "fact_race_result contains null values "
            "in critical metrics."
        )

    if (fact_race_result["points"] < 0).any():
        raise ValueError(
            "fact_race_result contains negative points."
        )

    if (fact_race_result["laps"] < 0).any():
        raise ValueError(
            "fact_race_result contains negative lap counts."
        )

    winners_per_event = (
        fact_race_result
        .groupby("event_key")["is_winner"]
        .sum()
    )

    if not winners_per_event.eq(1).all():
        raise ValueError(
            "Each event must have exactly one winner."
        )


def save_fact_race_result(
    fact_race_result: pd.DataFrame,
) -> None:
    """
    Saves the race result fact table in the Gold layer.
    """

    GOLD_FACT_RACE_RESULT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fact_race_result.to_parquet(
        GOLD_FACT_RACE_RESULT_PATH,
        index=False,
    )


def main() -> None:
    print("Starting fact_race_result build.")

    required_paths = [
        SILVER_RACE_RESULTS_PATH,
        GOLD_DIM_EVENT_PATH,
        GOLD_DIM_DRIVER_PATH,
        GOLD_DIM_TEAM_PATH,
    ]

    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(
                f"Required dataset not found: {path}"
            )

    silver_race_results = pd.read_parquet(
        SILVER_RACE_RESULTS_PATH
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

    print("fact_race_result build completed.")
    print(f"Rows: {len(fact_race_result)}")
    print(
        f"Columns: {len(fact_race_result.columns)}"
    )
    print(
        f"Output: {GOLD_FACT_RACE_RESULT_PATH}"
    )

    print("\n" + "=" * 80)
    print("Validating complete Gold Star Schema")

    validate_star_schema(
        dim_event=dim_event,
        dim_driver=dim_driver,
        dim_team=dim_team,
        fact_race_result=fact_race_result,
    )


if __name__ == "__main__":
    main()