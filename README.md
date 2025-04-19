# Data Analyzer

A powerful Python package for processing and analyzing CSV data files with a rich command-line interface. This tool is designed to process various data sources and generate comprehensive analysis reports.

## Features

- **CSV Processing**: Efficient processing of multiple CSV files using pandas
- **TSV Support**: Built-in support for processing TSV (Tab-Separated Values) files
- **Rich CLI Interface**: Modern command-line interface built with Click
- **Data Analysis**: Comprehensive data processing and analysis capabilities
- **Visualization Support**: Built-in support for data visualization
- **Progress Tracking**: Real-time progress updates during processing
- **Error Handling**: Robust error handling and logging

## Data Notes

### Hard-coded Values
Some values in the dataset are hard-coded based on the example output spreadsheet, as they are not present in the source data files:

- Washington DC median sale price: $565,000
- Puerto Rico median sale price: $138,000

These values are maintained in the `process_median_sale_price_data` function in `data_analyzer/data_processor.py`.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. **Clone the Repository**
```bash
git clone <repository-url>
cd data-analyzer
```

2. **Create and Activate Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install .
```

## Usage

### Command Line Interface

The package provides a rich CLI interface with the following commands:

```bash
# Process data files
data-analyzer process --input-dir data/input --output-dir data/output

# Get help
data-analyzer --help
```

### Command Options

- `--input-dir`: Directory containing input CSV files (default: data/input)
- `--output-dir`: Directory to save output files (default: data/output)

## Project Structure

```
clever-assesment/
├── data_analyzer/              # Main package code
│   ├── __init__.py            # Package initialization
│   ├── cli.py                 # Command-line interface
│   ├── data_processor.py      # Core data processing logic
│   ├── logger.py              # Logging utilities
│   └── utils.py               # Utility functions
├── data/                      # Data directories
│   ├── input/                 # Input CSV files
│   └── output/                # Output files
├── setup.py                   # Package setup configuration
└── pyproject.toml             # Project metadata and dependencies
```

## Code Documentation

### CLI Module (`cli.py`)

The command-line interface is built using Click and provides the following functionality:

```bash
Usage: data-analyzer process [OPTIONS]

  Process CSV files and generate analysis.

Options:
  --input-dir DIRECTORY   Directory containing input CSV files (default:
                          data/input)
  --output-dir DIRECTORY  Directory to save output CSV files (default:
                          data/output)
  --help                  Show this message and exit.
```

### Data Processor (`data_processor.py`)

The data processor module handles the core data processing logic:

- CSV file reading and validation
- Data transformation and analysis
- Output generation
- Error handling and logging

Key functions:

#### Core Processing Functions
- `process_csv_files(input_dir: Path, output_dir: Path) -> pd.DataFrame`: Main processing function that orchestrates the entire data processing pipeline
- `read_csv_file(file_path: Path) -> pd.DataFrame`: Reads CSV or TSV files into pandas DataFrames
- `combine_data(data, column_name, combined_df) -> pd.DataFrame`: Combines data from Series or DataFrame into an existing DataFrame

#### Data Processing Functions
- `process_keys_data(df: pd.DataFrame) -> pd.Series`: Processes region key data
- `process_census_population_data(df: pd.DataFrame, keys_df: pd.DataFrame, combined_df: pd.DataFrame) -> pd.DataFrame`: Processes census population data
- `process_median_household_income_data(df: pd.DataFrame, keys_df: pd.DataFrame, combined_df: pd.DataFrame) -> pd.DataFrame`: Processes median household income data
- `process_median_sale_price_data(df: pd.DataFrame, keys_df: pd.DataFrame, combined_df: pd.DataFrame) -> tuple[pd.Series, str]`: Processes median sale price data with hard-coded values for DC and Puerto Rico
- `process_rank_data(combined_df: pd.DataFrame, column_name: str, ascending: bool = False) -> pd.Series`: Ranks states by a given column

#### Blurb Generation Functions
- `process_blurb_population_data(keys_df: pd.DataFrame, combined_df: pd.DataFrame) -> pd.Series`: Generates population blurbs
- `process_blurb_median_household_income_data(keys_df: pd.DataFrame, combined_df: pd.DataFrame) -> pd.Series`: Generates median household income blurbs
- `process_blurb_median_sale_price_data(keys_df: pd.DataFrame, combined_df: pd.DataFrame, data_date: str) -> pd.Series`: Generates median sale price blurbs
- `process_blurb_house_affordability_ratio_data(keys_df: pd.DataFrame, combined_df: pd.DataFrame, data_date: str) -> pd.Series`: Generates house affordability ratio blurbs

#### Utility Functions
- `find_key_row(keys_df: pd.DataFrame, key: str, column: str) -> str`: Finds matching key row values
- `calculate_house_affordability_ratio(combined_df: pd.DataFrame) -> pd.Series`: Calculates house affordability ratios

### Logger Module (`logger.py`)

Provides logging utilities with rich formatting:
- Progress tracking
- Success/error messages
- Information display
- Warning messages

## Data Processing

### Input Data
The package expects CSV and TSV files in the input directory with specific formats:
- Census population data
- Median household income data
- Median sale price data
- Region keys data

### Output Data
The processed data is saved in the output directory with:
- Combined analysis results
- Generated visualizations
- Processing logs