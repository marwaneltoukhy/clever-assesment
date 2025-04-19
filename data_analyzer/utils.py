from pathlib import Path
from typing import List


def get_csv_files(directory: Path) -> List[Path]:
    """
    Get all CSV files in a directory.

    Args:
        directory: Directory to search for CSV files

    Returns:
        List of paths to CSV files

    Raises:
        FileNotFoundError: If input directory doesn't exist
        ValueError: If no CSV/TSV files are found in input directory
    """
    if not directory.exists():
        raise FileNotFoundError(f"Directory {directory} does not exist")

    csv_files = list(directory.glob("*.csv")) + list(directory.glob("*.tsv"))

    if not csv_files:
        raise ValueError(f"No CSV/TSV files found in {directory}")

    return csv_files


def create_output_directory(output_dir: Path) -> None:
    """
    Create an output directory if it doesn't exist.

    Args:
        output_dir: Path to the output directory

    Returns:
        None
    """
    output_dir.mkdir(parents=True, exist_ok=True)
