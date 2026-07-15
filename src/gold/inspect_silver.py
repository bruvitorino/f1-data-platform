from pathlib import Path

import pandas as pd


SILVER_EVENT_SCHEDULE_PATH = Path(
    "data/silver/event_schedule/event_schedule_2024.parquet"
)

SILVER_RACE_RESULTS_PATH = Path(
    "data/silver/race_results/race_results_2024.parquet"
)


def inspect_dataset(dataset_name: str, file_path: Path) -> None:
    """
    Displays structural information about a Silver dataset.

    This inspection is used during Gold data modeling to understand:
    - available columns;
    - data types;
    - row counts;
    - sample records;
    - candidate dimension and fact attributes.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Silver dataset not found: {file_path}"
        )

    dataframe = pd.read_parquet(file_path)

    print("=" * 80)
    print(f"SILVER DATASET: {dataset_name}")
    print("=" * 80)

    print(f"\nFile: {file_path}")
    print(f"Rows: {len(dataframe)}")
    print(f"Columns: {len(dataframe.columns)}")

    print("\nCOLUMN NAMES")
    print("-" * 80)

    for column in dataframe.columns:
        print(column)

    print("\nDATA TYPES")
    print("-" * 80)
    print(dataframe.dtypes.to_string())

    print("\nSAMPLE RECORDS")
    print("-" * 80)
    print(dataframe.head(3).to_string(index=False))

    print()


def main() -> None:
    print("Starting Silver datasets inspection for Gold modeling.\n")

    inspect_dataset(
        dataset_name="Event Schedule",
        file_path=SILVER_EVENT_SCHEDULE_PATH,
    )

    inspect_dataset(
        dataset_name="Race Results",
        file_path=SILVER_RACE_RESULTS_PATH,
    )

    print("Silver datasets inspection completed.")


if __name__ == "__main__":
    main()