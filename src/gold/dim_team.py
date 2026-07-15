from pathlib import Path

import pandas as pd

from src.gold.schema import DIM_TEAM_COLUMNS


SILVER_RACE_RESULTS_PATH = Path(
    "data/silver/race_results/race_results_2024.parquet"
)

GOLD_DIM_TEAM_PATH = Path(
    "data/gold/dimensions/dim_team/dim_team.parquet"
)


def build_dim_team(
    silver_race_results: pd.DataFrame,
) -> pd.DataFrame:
    """
    Builds the team dimension from Silver race results.

    Grain:
        One row per Formula 1 team.

    Natural key:
        team_id

    Surrogate key:
        team_key
    """

    team_columns = [
        "team_id",
        "team_name",
    ]

    dim_team = (
        silver_race_results[team_columns]
        .drop_duplicates(subset=["team_id"])
        .sort_values(by="team_id")
        .reset_index(drop=True)
    )

    dim_team["team_key"] = dim_team.index + 1

    dim_team = dim_team[DIM_TEAM_COLUMNS]

    return dim_team


def validate_dim_team(
    dim_team: pd.DataFrame,
) -> None:
    """
    Performs structural validations specific to dim_team.
    """

    if dim_team.empty:
        raise ValueError("dim_team cannot be empty.")

    if dim_team["team_key"].isna().any():
        raise ValueError(
            "dim_team contains null team keys."
        )

    if dim_team["team_key"].duplicated().any():
        raise ValueError(
            "dim_team contains duplicated team keys."
        )

    if dim_team["team_id"].isna().any():
        raise ValueError(
            "dim_team contains null team IDs."
        )

    if dim_team["team_id"].duplicated().any():
        raise ValueError(
            "dim_team contains duplicated team IDs."
        )

    critical_columns = [
        "team_key",
        "team_id",
        "team_name",
    ]

    if dim_team[critical_columns].isna().any().any():
        raise ValueError(
            "dim_team contains null values "
            "in critical columns."
        )


def save_dim_team(
    dim_team: pd.DataFrame,
) -> None:
    """
    Saves the team dimension in the Gold layer.
    """

    GOLD_DIM_TEAM_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dim_team.to_parquet(
        GOLD_DIM_TEAM_PATH,
        index=False,
    )


def main() -> None:
    print("Starting dim_team build.")

    if not SILVER_RACE_RESULTS_PATH.exists():
        raise FileNotFoundError(
            "Silver Race Results dataset not found: "
            f"{SILVER_RACE_RESULTS_PATH}"
        )

    silver_race_results = pd.read_parquet(
        SILVER_RACE_RESULTS_PATH
    )

    dim_team = build_dim_team(
        silver_race_results
    )

    validate_dim_team(dim_team)

    save_dim_team(dim_team)

    print("dim_team build completed.")
    print(f"Rows: {len(dim_team)}")
    print(f"Columns: {len(dim_team.columns)}")
    print(f"Output: {GOLD_DIM_TEAM_PATH}")


if __name__ == "__main__":
    main()