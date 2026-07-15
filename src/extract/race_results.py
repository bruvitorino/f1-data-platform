from pathlib import Path

import fastf1
import pandas as pd

from configs.settings import BRONZE_DATA_PATH, CURRENT_SEASON


EVENT_SCHEDULE_PATH = Path(
    "data/silver/event_schedule"
) / f"event_schedule_{CURRENT_SEASON}.parquet"

RACE_RESULTS_BRONZE_DIRECTORY = (
    Path(BRONZE_DATA_PATH) / "race_results"
)


def load_event_schedule(file_path: Path) -> pd.DataFrame:
    """
    Load the Silver event schedule used to determine which races
    must be extracted.

    Args:
        file_path (Path): Path to the Silver event schedule.

    Returns:
        pd.DataFrame: Formula 1 event schedule.
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"Event schedule file not found: {file_path}"
        )

    return pd.read_parquet(file_path)


def extract_race_results(
    year: int,
    round_number: int,
    event_name: str,
) -> pd.DataFrame:
    """
    Extract the race results for one Formula 1 round.

    Args:
        year (int): Formula 1 season.
        round_number (int): Championship round number.
        event_name (str): Race event name.

    Returns:
        pd.DataFrame: Raw race results with extraction metadata.
    """
    print(
        f"Extracting round {round_number}: {event_name}"
    )

    session = fastf1.get_session(
        year,
        round_number,
        "R",
    )

    session.load(
        laps=False,
        telemetry=False,
        weather=False,
        messages=False,
    )

    results = session.results.copy()
    results = results.reset_index(drop=True)

    results.insert(0, "Season", year)
    results.insert(1, "RoundNumber", round_number)
    results.insert(2, "EventName", event_name)

    return results

def extract_season_race_results(
    schedule: pd.DataFrame,
    year: int,
) -> pd.DataFrame:
    """
    Extract and consolidate race results for all rounds in a season.

    Args:
        schedule (pd.DataFrame): Silver event schedule.
        year (int): Formula 1 season.

    Returns:
        pd.DataFrame: Consolidated race results for the season.
    """
    extracted_results: list[pd.DataFrame] = []

    for race in schedule.itertuples(index=False):
        race_results = extract_race_results(
            year=year,
            round_number=int(race.round_number),
            event_name=race.event_name,
        )

        extracted_results.append(race_results)

    if not extracted_results:
        raise ValueError(
            f"No race results were extracted for season {year}."
        )

    return pd.concat(
        extracted_results,
        ignore_index=True,
    )


def save_race_results_to_bronze(
    race_results: pd.DataFrame,
    year: int,
) -> Path:
    """
    Save the raw season race results in the Bronze layer.

    Args:
        race_results (pd.DataFrame): Consolidated race results.
        year (int): Formula 1 season.

    Returns:
        Path: Location of the generated Parquet file.
    """
    RACE_RESULTS_BRONZE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        RACE_RESULTS_BRONZE_DIRECTORY
        / f"race_results_{year}.parquet"
    )

    race_results.to_parquet(
        output_path,
        index=False,
    )

    return output_path

def main() -> None:
    """Extract and save race results for the complete season."""

    schedule = load_event_schedule(EVENT_SCHEDULE_PATH)

    race_results = extract_season_race_results(
        schedule=schedule,
        year=CURRENT_SEASON,
    )

    output_path = save_race_results_to_bronze(
        race_results=race_results,
        year=CURRENT_SEASON,
    )

    print()
    print("Season race results extraction completed.")
    print(
        "Races extracted: "
        f"{race_results['RoundNumber'].nunique()}"
    )
    print(f"Rows: {len(race_results)}")
    print(f"Columns: {len(race_results.columns)}")
    print(f"Bronze file created: {output_path}")

if __name__ == "__main__":
    main()