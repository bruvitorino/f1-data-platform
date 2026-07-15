import pandas as pd
from src.quality.report_generator import generate_terminal_report
from src.quality.report_writer import save_report
def analyze_dataset(df: pd.DataFrame) -> dict:
    """
    Generate an initial data quality analysis for a DataFrame.

    Args:
        df (pd.DataFrame): Dataset to be analyzed.

    Returns:
        dict: Dataset quality information.
    """
    null_values = df.isnull().sum()
    total_cells = df.shape[0] * df.shape[1]

    analysis = {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "null_values": null_values.to_dict(),
        "columns_with_nulls": int((null_values > 0).sum()),
        "total_null_values": int(null_values.sum()),
        "null_percentage": round(
            (null_values.sum() / total_cells) * 100,
            2,
        ) if total_cells > 0 else 0.0,
        "duplicated_rows": int(df.duplicated().sum()),
        "duplicate_percentage": round(
            (df.duplicated().sum() / len(df)) * 100,
            2,
        ) if len(df) > 0 else 0.0,
        "empty_columns": df.columns[df.isnull().all()].tolist(),
        "single_value_columns": [
            column
            for column in df.columns
            if df[column].nunique(dropna=False) == 1
        ],
        "memory_usage_bytes": int(
            df.memory_usage(deep=True).sum()
        ),
    }

    return analysis


if __name__ == "__main__":
    dataset = pd.read_parquet(
        "data/bronze/event_schedule_2024.parquet"
    )

    analysis = analyze_dataset(dataset)
    formatted_report = generate_terminal_report(analysis)

    print(formatted_report)

    save_report(
        formatted_report,
        "reports/quality_report.txt",
    )