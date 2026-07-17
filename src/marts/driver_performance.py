from pathlib import Path

import pandas as pd

from src.marts.mart_validator import validate_driver_performance


GOLD_PATH = Path("data/gold")
MARTS_PATH = Path("data/marts")


def load_gold_datasets() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    fact_race_result = pd.read_parquet(
        GOLD_PATH
        / "facts"
        / "fact_race_result"
        / "fact_race_result_2024.parquet"
    )

    dim_event = pd.read_parquet(
        GOLD_PATH
        / "dimensions"
        / "dim_event"
        / "dim_event_2024.parquet"
    )

    dim_driver = pd.read_parquet(
        GOLD_PATH
        / "dimensions"
        / "dim_driver"
        / "dim_driver.parquet"
    )

    dim_team = pd.read_parquet(
        GOLD_PATH
        / "dimensions"
        / "dim_team"
        / "dim_team.parquet"
    )

    return fact_race_result, dim_event, dim_driver, dim_team


def build_driver_performance(
    fact_race_result: pd.DataFrame,
    dim_event: pd.DataFrame,
    dim_driver: pd.DataFrame,
    dim_team: pd.DataFrame,
) -> pd.DataFrame:

    driver_performance = fact_race_result.merge(
        dim_event,
        on="event_key",
        how="left",
    )

    driver_performance = driver_performance.merge(
        dim_driver,
        on="driver_key",
        how="left",
    )

    driver_performance = driver_performance.merge(
        dim_team,
        on="team_key",
        how="left",
    )

    selected_columns = [
        "event_key",
        "driver_key",
        "team_key",
        "season",
        "round_number",
        "event_name",
        "event_date",
        "country",
        "location",
        "driver_id",
        "driver_number",
        "driver_abbreviation",
        "driver_name",
        "country_code",
        "team_id",
        "team_name",
        "grid_position",
        "finish_position",
        "classified_position",
        "classified_position_numeric",
        "race_time_or_gap",
        "race_time_or_gap_ms",
        "status",
        "points",
        "laps",
        "positions_gained",
        "is_winner",
        "is_podium",
        "is_points_finish",
        "is_dnf",
    ]

    return driver_performance[selected_columns]


def save_driver_performance(
    driver_performance: pd.DataFrame,
    season: int,
) -> Path:

    output_path = (
        MARTS_PATH
        / "driver_performance"
        / f"driver_performance_{season}.parquet"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    driver_performance.to_parquet(
        output_path,
        index=False,
    )

    return output_path


def main() -> None:
    fact_race_result, dim_event, dim_driver, dim_team = (
        load_gold_datasets()
    )

    print("Gold datasets loaded successfully.")
    print(f"Fact race result rows: {len(fact_race_result)}")
    print(f"Dim event rows: {len(dim_event)}")
    print(f"Dim driver rows: {len(dim_driver)}")
    print(f"Dim team rows: {len(dim_team)}")

    driver_performance = build_driver_performance(
        fact_race_result,
        dim_event,
        dim_driver,
        dim_team,
    )

    print("\nDriver Performance Mart built successfully.")
    print(f"Rows: {len(driver_performance)}")
    print(f"Columns: {len(driver_performance.columns)}")

    validate_driver_performance(driver_performance)

    season = int(driver_performance["season"].iloc[0])

    output_path = save_driver_performance(
        driver_performance,
        season,
    )

    print("\nDriver Performance Mart saved successfully.")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()