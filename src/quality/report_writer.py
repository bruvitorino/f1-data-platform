def save_report(report: str, output_path: str) -> None:
    """
    Save a report to a text file.

    Args:
        report (str): Formatted report.
        output_path (str): File path where the report will be saved.
    """

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(report)