def generate_terminal_report(analysis: dict) -> str:
    """
    Generate a readable data quality report.

    Args:
        analysis (dict): Result returned by analyze_dataset().

    Returns:
        str: Formatted data quality report.
    """
    rows, columns = analysis["shape"]
    memory_kb = analysis["memory_usage_bytes"] / 1024

    lines = [
        "=" * 50,
        "DATA QUALITY REPORT",
        "=" * 50,
        "",
        "GENERAL INFORMATION",
        "-" * 50,
        f"Rows: {rows}",
        f"Columns: {columns}",
        f"Memory usage: {memory_kb:.2f} KB",
        "",
        "DATA QUALITY",
        "-" * 50,
        f"Duplicated rows: {analysis['duplicated_rows']}",
        f"Duplicate percentage: {analysis['duplicate_percentage']}%",
        f"Columns with nulls: {analysis['columns_with_nulls']}",
        f"Total null values: {analysis['total_null_values']}",
        f"Null percentage: {analysis['null_percentage']}%",
        "",
        "EMPTY COLUMNS",
        "-" * 50,
        str(analysis["empty_columns"]),
        "",
        "SINGLE VALUE COLUMNS",
        "-" * 50,
        str(analysis["single_value_columns"]),
        "",
        "NULL VALUES BY COLUMN",
        "-" * 50,
    ]

    for column, null_count in analysis["null_values"].items():
        if null_count > 0:
            lines.append(f"{column}: {null_count}")

    if analysis["total_null_values"] == 0:
        lines.append("No null values found.")

    return "\n".join(lines)
    