from pathlib import Path

import pandas as pd

from src.marts.mart_validator import validate_team_performance


MARTS_PATH = Path("data/marts")


def load_driver_performance(season: int) -> pd.DataFrame:
    input_path = (
        MARTS_PATH
        / "driver_performance"
        / f"driver_performance_{season}.parquet"
    )

    return pd.read_parquet(input_path)


def build_team_performance(
    driver_performance: pd.DataFrame,
) -> pd.DataFrame:

    team_performance = (
        driver_performance.groupby(
            [
                "event_key",
                "team_key",
                "season",
                "round_number",
                "event_name",
                "event_date",
                "country",
                "location",
                "team_id",
                "team_name",
            ],
            as_index=False,
        )
        .agg(
            drivers_count=("driver_key", "nunique"),
            team_points=("points", "sum"),
            best_finish_position=("finish_position", "min"),
            average_finish_position=("finish_position", "mean"),
            wins=("is_winner", "sum"),
            podiums=("is_podium", "sum"),
            points_finishes=("is_points_finish", "sum"),
            dnfs=("is_dnf", "sum"),
            total_laps=("laps", "sum"),
            total_positions_gained=("positions_gained", "sum"),
        )
    )

    team_performance["average_finish_position"] = (
        team_performance["average_finish_position"].round(2)
    )

    team_performance = team_performance.sort_values(
        by=["round_number", "team_name"]
    ).reset_index(drop=True)

    return team_performance


def save_team_performance(
    team_performance: pd.DataFrame,
    season: int,
) -> Path:

    output_path = (
        MARTS_PATH
        / "team_performance"
        / f"team_performance_{season}.parquet"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    team_performance.to_parquet(
        output_path,
        index=False,
    )

    return output_path


def main() -> None:
    season = 2024

    driver_performance = load_driver_performance(season)

    print("Driver Performance Mart loaded successfully.")
    print(f"Rows: {len(driver_performance)}")

    team_performance = build_team_performance(
        driver_performance
    )

    print("\nTeam Performance Mart built successfully.")
    print(f"Rows: {len(team_performance)}")
    print(f"Columns: {len(team_performance.columns)}")
    print(team_performance.head())

    validate_team_performance(team_performance)

    output_path = save_team_performance(
        team_performance,
        season,
    )
    print("\nTeam Performance Mart saved successfully.")
    print(f"Output: {output_path}")
    


if __name__ == "__main__":
    main()