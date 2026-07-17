import pandas as pd


def validate_driver_performance(
    driver_performance: pd.DataFrame,
) -> None:

    if driver_performance.empty:
        raise ValueError(
            "Driver Performance Mart is empty."
        )

    expected_rows = 479

    if len(driver_performance) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} rows "
            f"but found {len(driver_performance)}."
        )

    expected_columns = 30

    if len(driver_performance.columns) != expected_columns:
        raise ValueError(
            f"Expected {expected_columns} columns "
            f"but found {len(driver_performance.columns)}."
        )

    duplicates = driver_performance.duplicated(
        subset=["event_key", "driver_key"]
    ).sum()

    if duplicates > 0:
        raise ValueError(
            f"Found {duplicates} duplicated records "
            "for the Driver Performance grain."
        )

    critical_columns = [
        "event_key",
        "driver_key",
        "team_key",
        "driver_name",
        "team_name",
        "event_name",
    ]

    nulls = (
        driver_performance[critical_columns]
        .isna()
        .sum()
        .sum()
    )

    if nulls > 0:
        raise ValueError(
            f"Found {nulls} null values "
            "in critical columns."
        )

    print("\nDriver Performance validation passed.")

def validate_team_performance(
    team_performance: pd.DataFrame,
) -> None:

    if team_performance.empty:
        raise ValueError(
            "Team Performance Mart is empty."
        )

    expected_rows = 240
    expected_columns = 20

    if len(team_performance) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} rows "
            f"but found {len(team_performance)}."
        )

    if len(team_performance.columns) != expected_columns:
        raise ValueError(
            f"Expected {expected_columns} columns "
            f"but found {len(team_performance.columns)}."
        )

    duplicates = team_performance.duplicated(
        subset=["event_key", "team_key"]
    ).sum()

    if duplicates > 0:
        raise ValueError(
            f"Found {duplicates} duplicated records "
            "for the Team Performance grain."
        )

    critical_columns = [
        "event_key",
        "team_key",
        "team_name",
        "event_name",
    ]

    nulls = (
        team_performance[critical_columns]
        .isna()
        .sum()
        .sum()
    )

    if nulls > 0:
        raise ValueError(
            f"Found {nulls} null values "
            "in critical columns."
        )

    invalid_driver_counts = (
        team_performance["drivers_count"] <= 0
    ).sum()

    if invalid_driver_counts > 0:
        raise ValueError(
            f"Found {invalid_driver_counts} rows "
            "with invalid drivers_count."
        )

    print("\nTeam Performance validation passed.")