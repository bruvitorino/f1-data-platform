from collections.abc import Callable

from src.extract.fastf1_client import (
    main as extract_event_schedule,
)
from src.extract.race_results import (
    main as extract_race_results,
)


def run_extraction(
    extraction_name: str,
    extraction_function: Callable[[], None],
) -> None:
    """Run one extraction step and display its status."""

    print("=" * 80)
    print(f"Starting extraction: {extraction_name}")

    try:
        extraction_function()

    except Exception as error:
        print(f"Extraction failed: {extraction_name}")
        raise RuntimeError(
            f"Bronze extraction failed: {extraction_name}"
        ) from error

    print(f"Extraction completed: {extraction_name}")
    print()


def run_event_schedule_extraction() -> None:
    """Extract the Formula 1 event schedule to the Bronze layer."""

    run_extraction(
        extraction_name="Event Schedule",
        extraction_function=extract_event_schedule,
    )


def run_race_results_extraction() -> None:
    """Extract the season race results to the Bronze layer."""

    run_extraction(
        extraction_name="Race Results",
        extraction_function=extract_race_results,
    )