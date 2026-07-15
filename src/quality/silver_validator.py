from collections.abc import Callable
from pathlib import Path

import pandas as pd

from src.quality.dataset_analysis import analyze_dataset
from src.quality.report_generator import generate_terminal_report
from src.quality.report_writer import save_report


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SILVER_EVENT_SCHEDULE_FILE = (
    PROJECT_ROOT
    / "data"
    / "silver"
    / "event_schedule"
    / "event_schedule_2024.parquet"
)

SILVER_RACE_RESULTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "silver"
    / "race_results"
    / "race_results_2024.parquet"
)

EVENT_SCHEDULE_REPORT_FILE = (
    PROJECT_ROOT
    / "reports"
    / "silver_event_schedule_quality_report.txt"
)

RACE_RESULTS_REPORT_FILE = (
    PROJECT_ROOT
    / "reports"
    / "silver_race_results_quality_report.txt"
)


EVENT_SCHEDULE_REQUIRED_COLUMNS = {
    "round_number",
    "country",
    "location",
    "official_event_name",
    "event_date",
    "event_name",
    "event_format",
    "session_1",
    "session_1_date_utc",
    "session_2",
    "session_2_date_utc",
    "session_3",
    "session_3_date_utc",
    "session_4",
    "session_4_date_utc",
    "session_5",
    "session_5_date_utc",
    "f1_api_support",
}

EVENT_SCHEDULE_CRITICAL_COLUMNS = [
    "round_number",
    "country",
    "location",
    "event_name",
    "event_date",
]

RACE_RESULTS_REQUIRED_COLUMNS = {
    "season",
    "round_number",
    "event_name",
    "driver_number",
    "driver_id",
    "driver_abbreviation",
    "driver_name",
    "team_id",
    "team_name",
    "country_code",
    "grid_position",
    "finish_position",
    "classified_position",
    "race_time",
    "status",
    "points",
    "laps",
}

RACE_RESULTS_CRITICAL_COLUMNS = [
    "season",
    "round_number",
    "event_name",
    "driver_number",
    "driver_id",
    "driver_name",
    "team_id",
    "team_name",
    "finish_position",
    "status",
    "points",
    "laps",
]


ValidationFunction = Callable[[pd.DataFrame], list[str]]


def validate_required_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
) -> list[str]:
    """Validate whether all required Silver columns are present."""

    available_columns = set(dataframe.columns)
    missing_columns = required_columns - available_columns

    if not missing_columns:
        return []

    return [
        f"Missing required columns: {sorted(missing_columns)}"
    ]


def validate_critical_nulls(
    dataframe: pd.DataFrame,
    critical_columns: list[str],
) -> list[str]:
    """Validate that critical business columns contain no null values."""

    null_counts = dataframe[critical_columns].isnull().sum()

    invalid_columns = {
        column: int(null_count)
        for column, null_count in null_counts.items()
        if null_count > 0
    }

    if not invalid_columns:
        return []

    return [
        f"Null values found in critical columns: {invalid_columns}"
    ]


def validate_event_schedule_row_count(
    dataframe: pd.DataFrame,
) -> list[str]:
    """Validate the expected number of races for the 2024 season."""

    expected_rows = 24
    actual_rows = len(dataframe)

    if actual_rows == expected_rows:
        return []

    return [
        (
            "Unexpected row count: "
            f"expected {expected_rows}, found {actual_rows}"
        )
    ]


def validate_round_numbers(
    dataframe: pd.DataFrame,
) -> list[str]:
    """Validate round-number uniqueness and expected range."""

    errors = []

    duplicated_rounds = dataframe[
        dataframe["round_number"].duplicated(keep=False)
    ]["round_number"].unique()

    if len(duplicated_rounds) > 0:
        errors.append(
            f"Duplicated round numbers: {duplicated_rounds.tolist()}"
        )

    expected_rounds = set(range(1, 25))
    actual_rounds = set(dataframe["round_number"].tolist())

    missing_rounds = expected_rounds - actual_rounds
    unexpected_rounds = actual_rounds - expected_rounds

    if missing_rounds:
        errors.append(
            f"Missing round numbers: {sorted(missing_rounds)}"
        )

    if unexpected_rounds:
        errors.append(
            f"Unexpected round numbers: {sorted(unexpected_rounds)}"
        )

    return errors


def validate_event_schedule(
    dataframe: pd.DataFrame,
) -> list[str]:
    """Run all business validations for the Silver event schedule."""

    errors = validate_required_columns(
        dataframe,
        EVENT_SCHEDULE_REQUIRED_COLUMNS,
    )

    if errors:
        return errors

    errors.extend(
        validate_event_schedule_row_count(dataframe)
    )

    errors.extend(
        validate_round_numbers(dataframe)
    )

    errors.extend(
        validate_critical_nulls(
            dataframe,
            EVENT_SCHEDULE_CRITICAL_COLUMNS,
        )
    )

    return errors


def validate_race_result_keys(
    dataframe: pd.DataFrame,
) -> list[str]:
    """Validate Race Results business-key uniqueness."""

    business_key = [
        "season",
        "round_number",
        "driver_number",
    ]

    duplicated_keys = dataframe.duplicated(
        subset=business_key,
        keep=False,
    )

    if not duplicated_keys.any():
        return []

    duplicated_records = dataframe.loc[
        duplicated_keys,
        business_key,
    ]

    return [
        (
            "Duplicated Race Results business keys:\n"
            f"{duplicated_records.to_string(index=False)}"
        )
    ]


def validate_race_result_rounds(
    dataframe: pd.DataFrame,
) -> list[str]:
    """Validate that all expected rounds exist in Race Results."""

    expected_rounds = set(range(1, 25))
    actual_rounds = set(dataframe["round_number"].tolist())

    missing_rounds = expected_rounds - actual_rounds
    unexpected_rounds = actual_rounds - expected_rounds

    errors = []

    if missing_rounds:
        errors.append(
            f"Missing Race Results rounds: {sorted(missing_rounds)}"
        )

    if unexpected_rounds:
        errors.append(
            f"Unexpected Race Results rounds: {sorted(unexpected_rounds)}"
        )

    return errors


def validate_race_result_positions(
    dataframe: pd.DataFrame,
) -> list[str]:
    """Validate final-position consistency for each race."""

    errors = []

    duplicated_positions = dataframe.duplicated(
        subset=[
            "season",
            "round_number",
            "finish_position",
        ],
        keep=False,
    )

    if duplicated_positions.any():
        errors.append(
            "Duplicated finish positions found within a race."
        )

    position_summary = (
        dataframe
        .groupby(
            ["season", "round_number"],
            as_index=False,
        )
        .agg(
            driver_count=("driver_number", "count"),
            minimum_position=("finish_position", "min"),
            maximum_position=("finish_position", "max"),
        )
    )

    invalid_races = position_summary[
        (position_summary["minimum_position"] != 1)
        | (
            position_summary["maximum_position"]
            != position_summary["driver_count"]
        )
    ]

    if not invalid_races.empty:
        errors.append(
            "Invalid finish-position sequence:\n"
            f"{invalid_races.to_string(index=False)}"
        )

    return errors


def validate_race_results(
    dataframe: pd.DataFrame,
) -> list[str]:
    """Run all business validations for Silver Race Results."""

    errors = validate_required_columns(
        dataframe,
        RACE_RESULTS_REQUIRED_COLUMNS,
    )

    if errors:
        return errors

    errors.extend(
        validate_critical_nulls(
            dataframe,
            RACE_RESULTS_CRITICAL_COLUMNS,
        )
    )

    errors.extend(
        validate_race_result_keys(dataframe)
    )

    errors.extend(
        validate_race_result_rounds(dataframe)
    )

    errors.extend(
        validate_race_result_positions(dataframe)
    )

    return errors


def validate_silver_dataset(
    dataset_name: str,
    input_path: Path,
    report_path: Path,
    validation_function: ValidationFunction,
) -> None:
    """Analyze, report and validate one Silver dataset."""

    print("-" * 80)
    print(f"Validating Silver dataset: {dataset_name}")

    if not input_path.exists():
        raise FileNotFoundError(
            f"Silver dataset not found: {input_path}"
        )

    dataframe = pd.read_parquet(input_path)

    analysis = analyze_dataset(dataframe)
    formatted_report = generate_terminal_report(analysis)

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    save_report(
        formatted_report,
        str(report_path),
    )

    validation_errors = validation_function(dataframe)

    print(formatted_report)
    print()
    print(
        f"Quality report saved: "
        f"{report_path.relative_to(PROJECT_ROOT)}"
    )

    if validation_errors:
        formatted_errors = "\n".join(
            f"- {error}"
            for error in validation_errors
        )

        raise ValueError(
            f"{dataset_name} Silver validation failed:\n"
            f"{formatted_errors}"
        )

    print(f"{dataset_name} Silver validation passed.")
    print()


def run_silver_quality_validation() -> None:
    """Run quality validation for every registered Silver dataset."""

    validate_silver_dataset(
        dataset_name="Event Schedule",
        input_path=SILVER_EVENT_SCHEDULE_FILE,
        report_path=EVENT_SCHEDULE_REPORT_FILE,
        validation_function=validate_event_schedule,
    )

    validate_silver_dataset(
        dataset_name="Race Results",
        input_path=SILVER_RACE_RESULTS_FILE,
        report_path=RACE_RESULTS_REPORT_FILE,
        validation_function=validate_race_results,
    )


def main() -> None:
    run_silver_quality_validation()


if __name__ == "__main__":
    main()