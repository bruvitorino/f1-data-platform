from pathlib import Path

import pandas as pd

GOLD_PATH = Path("data/gold")


def inspect_dataset(file_path: Path) -> None:
    """
    Inspect a Gold dataset and display basic information.
    """

    df = pd.read_parquet(file_path)

    print("\n" + "=" * 80)
    print(f"Dataset: {file_path.stem}")
    print("-" * 80)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for column in df.columns:
        print(f"- {column}")

    print("\nData Types:")
    print(df.dtypes)

    print("\nPreview:")
    print(df.head())

def main() -> None:
    
    """Inspect all Gold datasets."""
    
    for parquet_file in sorted(GOLD_PATH.rglob("*.parquet")):
        inspect_dataset(parquet_file)


if __name__ == "__main__":
    main()