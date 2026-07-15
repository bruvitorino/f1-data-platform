from pathlib import Path

import pandas as pd

from src.quality.dataset_analysis import analyze_dataset
from src.quality.report_generator import (
    generate_terminal_report,
)
from src.quality.report_writer import save_report


GOLD_DATASETS = {
    "dim_event": Path(
        "data/gold/dimensions/dim_event/"
        "dim_event_2024.parquet"
    ),
    "dim_driver": Path(
        "data/gold/dimensions/dim_driver/"
        "dim_driver.parquet"
    ),
    "dim_team": Path(
        "data/gold/dimensions/dim_team/"
        "dim_team.parquet"
    ),
    "fact_race_result": Path(
        "data/gold/facts/fact_race_result/"
        "fact_race_result_2024.parquet"
    ),
}

GOLD_REPORTS_PATH = Path(
    "reports/gold"
)


def generate_gold_quality_report(
    dataset_name: str,
    dataset_path: Path,
) -> None:
    """
    Generates and saves a quality report
    for a Gold dataset.
    """

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Gold dataset not found: {dataset_path}"
        )

    dataframe = pd.read_parquet(
        dataset_path
    )

    analysis = analyze_dataset(
        dataframe
    )

    formatted_report = generate_terminal_report(
        analysis
    )

    output_path = (
        GOLD_REPORTS_PATH
        / f"{dataset_name}_quality_report.txt"
    )

    print("\n" + "=" * 80)
    print(
        f"Generating quality report: {dataset_name}"
    )
    print("=" * 80)

    print(formatted_report)

    save_report(
        report=formatted_report,
        output_path=output_path,
    )

    print(
        f"\nQuality report saved: {output_path}"
    )


def run_gold_quality_reports() -> None:
    """
    Generates quality reports for every
    dataset in the Gold layer.
    """

    print(
        "Starting Gold data quality reports."
    )

    for dataset_name, dataset_path in (
        GOLD_DATASETS.items()
    ):
        generate_gold_quality_report(
            dataset_name=dataset_name,
            dataset_path=dataset_path,
        )

    print(
        "\nGold data quality reports "
        "completed successfully."
    )


def main() -> None:
    run_gold_quality_reports()


if __name__ == "__main__":
    main()