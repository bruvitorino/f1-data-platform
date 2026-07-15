from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"


def find_bronze_files() -> list[Path]:
    """Return all supported dataset files from the Bronze layer."""

    supported_extensions = {".csv", ".parquet", ".json"}

    return [
        file_path
        for file_path in BRONZE_DIR.rglob("*")
        if file_path.is_file()
        and file_path.suffix.lower() in supported_extensions
    ]


def load_dataset(file_path: Path) -> pd.DataFrame:
    """Load a dataset according to its file extension."""

    extension = file_path.suffix.lower()

    if extension == ".csv":
        return pd.read_csv(file_path)

    if extension == ".parquet":
        return pd.read_parquet(file_path)

    if extension == ".json":
        return pd.read_json(file_path)

    raise ValueError(f"Unsupported file format: {extension}")


def inspect_dataset(file_path: Path) -> None:
    """Display basic structural information about a Bronze dataset."""

    dataframe = load_dataset(file_path)

    print("=" * 80)
    print(f"File: {file_path.relative_to(PROJECT_ROOT)}")
    print(f"Rows: {dataframe.shape[0]}")
    print(f"Columns: {dataframe.shape[1]}")

    print("\nColumn names:")
    print(dataframe.columns.tolist())

    print("\nData types:")
    print(dataframe.dtypes)

    print("\nFirst rows:")
    print(dataframe.head())

    print()


def main() -> None:
    bronze_files = find_bronze_files()

    if not bronze_files:
        raise FileNotFoundError(
            f"No supported dataset files found in: {BRONZE_DIR}"
        )

    print(f"Bronze datasets found: {len(bronze_files)}\n")

    for file_path in bronze_files:
        inspect_dataset(file_path)


if __name__ == "__main__":
    main()