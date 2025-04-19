"""
Command-line interface for the Data Analyzer package.
"""

import click
from pathlib import Path
import pandas as pd

from rich.table import Table
from data_analyzer.data_processor import process_csv_files
from data_analyzer.time_series_analyzer import analyze_time_series
from data_analyzer.logger import (
    print_header,
    print_success,
    print_error,
    print_info,
    print_warning,
    console,
)


def display_results(processed_df: pd.DataFrame) -> None:
    """Display a summary of the processed DataFrame."""
    table = Table(title="Processed DataFrame Summary", style="cyan")
    table.add_column("Property", style="cyan")
    table.add_column("Value", justify="right", style="green")

    # Display shape of the final DataFrame
    table.add_row(
        "Output File", "output.csv"  # Assuming the output is always output.csv
    )
    table.add_row("Total Rows", str(len(processed_df)))
    table.add_row("Total Columns", str(len(processed_df.columns)))

    console.print()
    console.print(table)


@click.group()
def cli():
    """Data Analyzer CLI."""
    pass


@cli.command()
@click.option(
    "--input-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default="data/input",
    help="Directory containing input CSV files (default: data/input)",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default="data/output",
    help="Directory to save output CSV files (default: data/output)",
)
def process(input_dir: Path, output_dir: Path) -> None:
    """Process CSV files and generate analysis."""
    output_dir.mkdir(parents=True, exist_ok=True)

    print_header("Data Analyzer")
    print_info(f"Input directory: {input_dir}")
    print_info(f"Output directory: {output_dir}")

    try:
        processed_data = process_csv_files(input_dir, output_dir)
        display_results(processed_data)

        print_success("Processing completed successfully!")
    except Exception as e:
        print_error(f"Error during processing: {str(e)}")


@cli.command()
@click.option(
    "--input-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default="data/input",
    help="Directory containing input CSV files (default: data/input)",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default="data/output/time_series",
    help="Directory to save time series analysis results (default: data/output/time_series)",
)
def analyze_timeseries(input_dir: Path, output_dir: Path) -> None:
    """Perform time series analysis on Redfin median sale price data."""
    print_header("Time Series Analysis")
    print_info(f"Input directory: {input_dir}")
    print_info(f"Output directory: {output_dir}")

    try:
        analyze_time_series(input_dir, output_dir)
        print_success("Time series analysis completed successfully!")
    except Exception as e:
        print_error(f"Error during time series analysis: {str(e)}")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
