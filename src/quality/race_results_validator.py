import pandas as pd

from src.quality.dataset_analysis import analyze_dataset
from src.quality.report_generator import generate_terminal_report
from src.quality.report_writer import save_report

QUALITY_REPORT_PATH = (
    "reports/bronze_race_results_quality_report.txt"
)

MIN_DRIVERS_PER_RACE = 18
MAX_DRIVERS_PER_RACE = 22

BUSINESS_KEY = [
    "Season",
    "RoundNumber",
    "DriverNumber",
]

REQUIRED_COLUMNS = [
    "Season",
    "RoundNumber",
    "EventName",
    "DriverNumber",
    "FullName",
    "TeamName",
    "Position",
]


def validate_duplicate_keys(
    race_results: pd.DataFrame,
) -> None:
    """
    Validate that the race results business key is unique.

    Args:
        race_results (pd.DataFrame): Bronze race results dataset.

    Raises:
        ValueError: If duplicated business keys are found.
    """
    duplicated_rows = race_results.duplicated(
        subset=BUSINESS_KEY,
        keep=False,
    )

    duplicated_count = int(duplicated_rows.sum())

    if duplicated_count > 0:
        duplicated_records = race_results.loc[
            duplicated_rows,
            BUSINESS_KEY,
        ]

        raise ValueError(
            "Duplicated business keys found.\n"
            f"Duplicated rows: {duplicated_count}\n"
            f"{duplicated_records.to_string(index=False)}"
        )

    print("Duplicate business key validation passed.")

def validate_expected_rounds(
    race_results: pd.DataFrame,
    event_schedule: pd.DataFrame,
) -> None:
    """Validate that all expected championship rounds were extracted."""

    expected_rounds = set(
        event_schedule["round_number"].astype(int)
    )

    actual_rounds = set(
        race_results["RoundNumber"].astype(int)
    )

    missing_rounds = expected_rounds - actual_rounds
    unexpected_rounds = actual_rounds - expected_rounds

    if missing_rounds or unexpected_rounds:
        raise ValueError(
            "Round validation failed.\n"
            f"Missing rounds: {sorted(missing_rounds)}\n"
            f"Unexpected rounds: {sorted(unexpected_rounds)}"
        )

    print("Expected rounds validation passed.")

def validate_position_values(
    race_results: pd.DataFrame,
) -> None:
    """Validate final position values for each race."""

    null_positions = race_results["Position"].isna()

    if null_positions.any():
        raise ValueError(
            "Position validation failed.\n"
            f"Null positions: {int(null_positions.sum())}"
        )

    invalid_positions = race_results[
        race_results["Position"] < 1
    ]

    if not invalid_positions.empty:
        raise ValueError(
            "Position validation failed.\n"
            "Positions lower than 1 were found.\n"
            f"{invalid_positions[
                ['Season', 'RoundNumber', 'DriverNumber', 'Position']
            ].to_string(index=False)}"
        )

    duplicated_positions = race_results.duplicated(
        subset=[
            "Season",
            "RoundNumber",
            "Position",
        ],
        keep=False,
    )

    if duplicated_positions.any():
        duplicated_records = race_results.loc[
            duplicated_positions,
            [
                "Season",
                "RoundNumber",
                "DriverNumber",
                "Position",
            ],
        ]

        raise ValueError(
            "Position validation failed.\n"
            "Duplicated positions were found in the same race.\n"
            f"{duplicated_records.to_string(index=False)}"
        )

    race_position_summary = (
        race_results
        .groupby(
            ["Season", "RoundNumber"],
            as_index=False,
        )
        .agg(
            driver_count=("DriverNumber", "count"),
            minimum_position=("Position", "min"),
            maximum_position=("Position", "max"),
        )
    )

    invalid_races = race_position_summary[
        (race_position_summary["minimum_position"] != 1)
        | (
            race_position_summary["maximum_position"]
            != race_position_summary["driver_count"]
        )
    ]

    if not invalid_races.empty:
        raise ValueError(
            "Position validation failed.\n"
            "Position sequences do not match the number of drivers.\n"
            f"{invalid_races.to_string(index=False)}"
        )

    print("Position values validation passed.")

def validate_drivers_per_race(
    race_results: pd.DataFrame,
) -> None:
    """Validate that each race has a plausible number of drivers."""

    drivers_per_race = (
        race_results
        .groupby(
            ["Season", "RoundNumber", "EventName"],
            as_index=False,
        )
        .agg(
            driver_count=("DriverNumber", "count"),
        )
    )

    invalid_races = drivers_per_race[
        (drivers_per_race["driver_count"] < MIN_DRIVERS_PER_RACE)
        | (drivers_per_race["driver_count"] > MAX_DRIVERS_PER_RACE)
    ]

    if not invalid_races.empty:
        raise ValueError(
            "Drivers per race validation failed.\n"
            f"Expected between {MIN_DRIVERS_PER_RACE} "
            f"and {MAX_DRIVERS_PER_RACE} drivers.\n"
            f"{invalid_races.to_string(index=False)}"
        )

    print("Drivers per race validation passed.")

def generate_bronze_quality_report(
    race_results: pd.DataFrame,
) -> None:
    """Generate and save the generic Bronze quality report."""

    analysis = analyze_dataset(race_results)

    formatted_report = generate_terminal_report(
        analysis
    )

    print()
    print(formatted_report)
    print()

    save_report(
        formatted_report,
        QUALITY_REPORT_PATH,
    )

    print(
        f"Quality report saved: {QUALITY_REPORT_PATH}"
    )
    


def validate_required_columns(
    race_results: pd.DataFrame,
) -> None:
    """Validate that all required columns are present."""

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in race_results.columns
    ]

    if missing_columns:
        raise ValueError(
            "Required columns validation failed.\n"
            f"Missing columns: {missing_columns}"
        )

    print("Required columns validation passed.")

def main() -> None:
    """Run Race Results Bronze validations."""

    race_results_path = (
        "data/bronze/race_results/"
        "race_results_2024.parquet"
    )

    event_schedule_path = (
        "data/silver/event_schedule/"
        "event_schedule_2024.parquet"
    )

    race_results = pd.read_parquet(race_results_path)
    event_schedule = pd.read_parquet(event_schedule_path)

    validate_required_columns(race_results)

    validate_duplicate_keys(race_results)

    validate_expected_rounds(
        race_results,
        event_schedule,
    )

    validate_drivers_per_race(race_results)
    validate_position_values(race_results)
    
    generate_bronze_quality_report(race_results)

if __name__ == "__main__":
    main()