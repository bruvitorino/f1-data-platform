from pathlib import Path

import fastf1

from configs.settings import BRONZE_DATA_PATH, CURRENT_SEASON


def get_event_schedule(year: int):
    """
    Get the Formula 1 event schedule for a given season.

    Args:
        year (int): Formula 1 season year.

    Returns:
        pandas.DataFrame: Event schedule returned by FastF1.
    """
    schedule = fastf1.get_event_schedule(year)
    return schedule


def save_schedule_to_bronze(schedule, year: int) -> Path:
    """
    Save the raw event schedule in the Bronze layer as a Parquet file.

    Args:
        schedule: Event schedule returned by FastF1.
        year (int): Formula 1 season year.

    Returns:
        Path: Location of the generated Parquet file.
    """
    bronze_directory = Path(BRONZE_DATA_PATH)
    bronze_directory.mkdir(parents=True, exist_ok=True)

    output_path = bronze_directory / f"event_schedule_{year}.parquet"

    schedule.to_parquet(output_path, index=False)

    return output_path


if __name__ == "__main__":
    schedule = get_event_schedule(CURRENT_SEASON)
    saved_file = save_schedule_to_bronze(schedule, CURRENT_SEASON)

    print(f"Bronze file created: {saved_file}")