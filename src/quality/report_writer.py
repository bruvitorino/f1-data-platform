from pathlib import Path


def save_report(
    report: str,
    output_path: str | Path,
) -> None:
    """
    Saves a text report to the specified path.

    The parent directory is created automatically
    when it does not exist.

    Args:
        report:
            Formatted report content.

        output_path:
            File path where the report will be saved.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        report,
        encoding="utf-8",
    )