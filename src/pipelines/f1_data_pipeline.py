import logging

from src.gold.gold_pipeline import run_gold_pipeline
from src.marts.mart_pipeline import run_mart_pipeline
from src.pipelines.extract_pipeline import (
    run_event_schedule_extraction,
    run_race_results_extraction,
)
from src.transform.transform_pipeline import (
    run_event_schedule_transformation,
    run_race_results_transformation,
    run_silver_validation,
)
from src.utils.execution_timer import measure_execution_time
from src.utils.logging_config import configure_logging


logger = logging.getLogger(__name__)


def run_f1_data_pipeline() -> None:
    """Run the complete F1 Data Platform pipeline."""

    logger.info("Starting F1 Data Platform Pipeline")

    # ==========================================================================
    # Event Schedule
    # ==========================================================================

    logger.info("Starting workflow: Event Schedule")

    event_schedule_duration = measure_execution_time(
        lambda: (
            run_event_schedule_extraction(),
            run_event_schedule_transformation(),
        )
    )

    logger.info(
        "Workflow completed: Event Schedule (%.2f seconds)",
        event_schedule_duration,
    )

    # ==========================================================================
    # Race Results
    # ==========================================================================

    logger.info("Starting workflow: Race Results")

    race_results_duration = measure_execution_time(
        lambda: (
            run_race_results_extraction(),
            run_race_results_transformation(),
        )
    )

    logger.info(
        "Workflow completed: Race Results (%.2f seconds)",
        race_results_duration,
    )

    # ==========================================================================
    # Silver Validation
    # ==========================================================================

    logger.info("Starting step: Silver Layer Validation")

    silver_duration = measure_execution_time(
        run_silver_validation
    )

    logger.info(
        "Step completed: Silver Layer Validation (%.2f seconds)",
        silver_duration,
    )

    # ==========================================================================
    # Gold Layer
    # ==========================================================================

    logger.info("Starting step: Gold Layer")

    gold_duration = measure_execution_time(
        run_gold_pipeline
    )

    logger.info(
        "Step completed: Gold Layer (%.2f seconds)",
        gold_duration,
    )

    # ==========================================================================
    # Data Marts
    # ==========================================================================

    logger.info("Starting step: Data Marts Layer")

    marts_duration = measure_execution_time(
        run_mart_pipeline
    )

    logger.info(
        "Step completed: Data Marts Layer (%.2f seconds)",
        marts_duration,
    )

    logger.info("F1 Data Platform Pipeline completed successfully")


def main() -> None:
    """Configure logging and run the complete F1 Data Platform pipeline."""

    configure_logging()
    run_f1_data_pipeline()


if __name__ == "__main__":
    main()