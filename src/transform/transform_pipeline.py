from collections.abc import Callable

from src.transform.event_schedule import main as transform_event_schedule

from src.transform.race_results import (
    main as transform_race_results,
)

from src.quality.silver_validator import (
    run_silver_quality_validation,
)


Transformation = tuple[str, Callable[[], None]]


TRANSFORMATIONS = [
    (
        "Event Schedule",
        transform_event_schedule,
    ),
    (
        "Race Results",
        transform_race_results,
    ),
]


def run_transformation(
    transformation_name: str,
    transformation_function: Callable[[], None],
) -> None:
    """Run one Silver transformation and display its status."""

    print("=" * 80)
    print(f"Starting transformation: {transformation_name}")

    try:
        transformation_function()

    except Exception as error:
        print(f"Transformation failed: {transformation_name}")
        raise RuntimeError(
            f"Silver transformation failed: {transformation_name}"
        ) from error

    print(f"Transformation completed: {transformation_name}")
    print()


def run_event_schedule_transformation() -> None:
    """Run the Event Schedule Bronze-to-Silver transformation."""

    run_transformation(
        transformation_name="Event Schedule",
        transformation_function=transform_event_schedule,
    )


def run_race_results_transformation() -> None:
    """Run the Race Results Bronze-to-Silver transformation."""

    run_transformation(
        transformation_name="Race Results",
        transformation_function=transform_race_results,
    )


def run_silver_validation() -> None:
    """Run data quality validation for the complete Silver layer."""

    print("=" * 80)
    print("Starting Silver data quality validation.")

    run_silver_quality_validation()

    print("Silver data quality validation completed.")
    print()


def run_transform_pipeline() -> None:
    """Run all registered Bronze-to-Silver transformations."""

    print("Starting Silver transformation pipeline.\n")

    for transformation_name, transformation_function in TRANSFORMATIONS:
        run_transformation(
            transformation_name,
            transformation_function,
        )

    run_silver_validation()

    print("=" * 80)
    print("Silver transformation pipeline completed successfully.")
    print(f"Transformations executed: {len(TRANSFORMATIONS)}")


def main() -> None:
    """Run the complete Silver transformation pipeline."""

    run_transform_pipeline()


if __name__ == "__main__":
    main()
