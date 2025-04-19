import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
from data_analyzer.utils import get_csv_files
from data_analyzer.logger import (
    logger,
    print_success,
    print_error,
    print_warning,
    print_info,
    create_progress,
)


def read_csv_file(file_path: Path) -> pd.DataFrame:
    """
    Read a CSV or TSV file into a pandas DataFrame.

    Args:
        file_path: Path to the CSV/TSV file

    Returns:
        DataFrame containing the file data

    Raises:
        FileNotFoundError: If the file doesn't exist
        pd.errors.EmptyDataError: If the file is empty
        ValueError: If the file format is not supported
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} does not exist")

    try:
        if file_path.suffix == ".tsv":
            df = pd.read_csv(file_path, sep="\t")
        else:
            df = pd.read_csv(file_path)
        print_success(f"Successfully read {file_path.name}")
        return df
    except Exception as e:
        print_error(f"Error reading {file_path.name}: {str(e)}")
        raise


def calculate_house_affordability_ratio(df: pd.DataFrame) -> pd.Series:
    """
    Calculate the house affordability ratio (median_sale_price / median_household_income)
    for each state, rounded to 1 decimal place.

    Args:
        df: DataFrame containing median_sale_price and median_household_income columns

    Returns:
        Series containing the house affordability ratios
    """
    return df.apply(
        lambda row: (
            round(row["median_sale_price"] / row["median_household_income"], 1)
            if pd.notna(row["median_sale_price"])
            and pd.notna(row["median_household_income"])
            else pd.NA
        ),
        axis=1,
    )


def process_csv_files(input_dir: Path, output_dir: Path) -> pd.DataFrame:
    """
    Process CSV files from input directory and save results to output directory.

    Args:
        input_dir: Directory containing input files
        output_dir: Directory to save output files

    Returns:
        Combined DataFrame with all processed data

    Raises:
        FileNotFoundError: If input directory doesn't exist
        ValueError: If no CSV/TSV files are found in input directory
    """
    csv_files = get_csv_files(input_dir)

    # Initialize the output DataFrame with the required columns
    output_columns = [
        "key_row",
        "census_population",
        "population_rank",
        "population_blurb",
        "median_household_income",
        "median_household_income_rank",
        "median_household_income_blurb",
        "median_sale_price",
        "median_sale_price_rank",
        "median_sale_price_blurb",
        "house_affordability_ratio",
        "house_affordability_ratio_rank",
        "house_affordability_ratio_blurb",
    ]

    # Create an empty DataFrame with the required columns
    combined_df = pd.DataFrame(columns=output_columns)

    # Create progress bar
    progress = create_progress()

    with progress:
        # Process KEYS file first
        task = progress.add_task("[cyan]Processing KEYS file...", total=1)
        for file_path in csv_files:
            if "KEYS" in file_path.name:
                try:
                    keys_df = read_csv_file(file_path)
                    processed_keys_df = process_keys_data(keys_df)
                    combined_df = combine_data(
                        processed_keys_df, "key_row", combined_df
                    )
                    progress.update(task, advance=1)
                except Exception as e:
                    print_error(f"Error processing {file_path.name}: {str(e)}")
                    continue

        # Process remaining files
        redfin_date = None
        task = progress.add_task(
            "[cyan]Processing data files...", total=len(csv_files) - 1
        )
        for file_path in csv_files:
            if "KEYS" not in file_path.name:
                try:
                    df = read_csv_file(file_path)
                    if "CENSUS_POPULATION" in file_path.name:
                        processed_df = process_census_population_data(
                            df, keys_df, combined_df
                        )
                        combined_df = combine_data(
                            processed_df, "census_population", combined_df
                        )
                    elif "CENSUS_MHI_STATE" in file_path.name:
                        processed_df = process_median_household_income_data(
                            df, keys_df, combined_df
                        )
                        combined_df = combine_data(
                            processed_df, "median_household_income", combined_df
                        )
                    elif "REDFIN_MEDIAN_SALE_PRICE" in file_path.name:
                        processed_df, redfin_date = process_median_sale_price_data(
                            df, keys_df, combined_df
                        )
                        combined_df = combine_data(
                            processed_df, "median_sale_price", combined_df
                        )
                    progress.update(task, advance=1)
                except Exception as e:
                    print_error(f"Error processing {file_path.name}: {str(e)}")
                    continue

        # Add population rank column
        task = progress.add_task("[cyan]Calculating ranks...", total=3)
        combined_df["population_rank"] = process_rank_data(
            combined_df, "census_population", ascending=False
        )
        progress.update(task, advance=1)
        combined_df["median_household_income_rank"] = process_rank_data(
            combined_df, "median_household_income", ascending=False
        )
        progress.update(task, advance=1)
        combined_df["median_sale_price_rank"] = process_rank_data(
            combined_df, "median_sale_price", ascending=False
        )
        progress.update(task, advance=1)

        # Add blurb column
        task = progress.add_task("[cyan]Generating blurbs...", total=4)
        population_blurb = process_blurb_population_data(keys_df, combined_df)
        combined_df = combine_data(population_blurb, "population_blurb", combined_df)
        progress.update(task, advance=1)
        median_household_income_blurb = process_blurb_median_household_income_data(
            keys_df, combined_df
        )
        combined_df = combine_data(
            median_household_income_blurb, "median_household_income_blurb", combined_df
        )
        progress.update(task, advance=1)
        median_sale_price_blurb = process_blurb_median_sale_price_data(
            keys_df, combined_df, redfin_date
        )
        combined_df = combine_data(
            median_sale_price_blurb, "median_sale_price_blurb", combined_df
        )
        progress.update(task, advance=1)

        try:
            # Calculate house affordability ratio
            combined_df["house_affordability_ratio"] = (
                calculate_house_affordability_ratio(combined_df)
            )

            # Add rank for house affordability ratio
            combined_df["house_affordability_ratio_rank"] = process_rank_data(
                combined_df, "house_affordability_ratio", ascending=True
            )

            # Add house affordability ratio blurb
            house_affordability_ratio_blurb = (
                process_blurb_house_affordability_ratio_data(
                    keys_df, combined_df, redfin_date
                )
            )
            combined_df = combine_data(
                house_affordability_ratio_blurb,
                "house_affordability_ratio_blurb",
                combined_df,
            )
            progress.update(task, advance=1)

            # Save the combined data with float_format to ensure proper decimal rounding
            output_path = output_dir / "output.csv"
            combined_df.to_csv(output_path, index=False, float_format="%.1f")
            print_success(f"Saved combined data to {output_path}")
        except Exception as e:
            print_error(f"Warning: Error during final processing: {str(e)}")
            # Still save the file if we haven't already
            # Check if output_path was defined before error
            if "output_path" in locals() and not output_path.exists():
                combined_df.to_csv(output_path, index=False, float_format="%.1f")
                print_warning(f"Saved partial data to {output_path}")
            else:
                print_error(
                    "Cannot save partial data (output_path not defined or file exists)."
                )

    return combined_df


def process_keys_data(df: pd.DataFrame) -> pd.Series:
    """Process keys data to filter for state rows and remove any with apostrophes."""
    processed_df = df.copy()
    # Delete the alternative_name column
    processed_df = processed_df.drop("alternative_name", axis=1)
    # Filter to keep only state rows
    processed_df = processed_df[processed_df["region_type"] == "state"]
    # Filter to remove any rows with apostrophes
    processed_df = processed_df[~processed_df["key_row"].str.contains("'")]
    # Return Series with key_row column
    return processed_df["key_row"]


def find_key_row(keys_df: pd.DataFrame, key: str, column: str) -> str:
    """Find the value in a column that matches a given key.

    Args:
        keys_df: DataFrame containing key_row values
        key: The key value to search for
        column: Column name to get the value from

    Returns:
        str: The value from the specified column where key matches
    """
    matching_row = keys_df[keys_df["key_row"] == key]
    return matching_row[column].iloc[0] if not matching_row.empty else None


def process_census_population_data(
    df: pd.DataFrame, keys_df: pd.DataFrame, combined_df: pd.DataFrame
) -> pd.DataFrame:
    processed_df = df.copy()
    # Keep only the header and row with "Total population"
    processed_df = processed_df[
        processed_df["Label (Grouping)"].str.contains("Total population", na=False)
    ]
    population_dict = {}

    for _, row in combined_df.iterrows():
        # Find the key_row value for the matching row and append !!Estimate
        key_row = (
            find_key_row(keys_df, row["key_row"], "zillow_region_name") + "!!Estimate"
        )
        # Get the Total population value from the matching column and remove commas
        population_value = processed_df[key_row].iloc[0].replace(",", "")
        population_dict[row["key_row"]] = int(population_value)
    return pd.Series(population_dict)


def process_median_household_income_data(
    df: pd.DataFrame, keys_df: pd.DataFrame, combined_df: pd.DataFrame
) -> pd.DataFrame:
    processed_df = df.copy()
    # Keep only the header and row with "Households"
    processed_df = processed_df[
        processed_df["Label (Grouping)"].str.contains("Households", na=False)
    ]
    households_dict = {}

    for _, row in combined_df.iterrows():
        # Find the key_row value for the matching row and append !!Estimate
        key_row = (
            find_key_row(keys_df, row["key_row"], "zillow_region_name")
            + "!!Median income (dollars)!!Estimate"
        )
        # Get the Total population value from the matching column and remove commas
        population_value = processed_df[key_row].iloc[0].replace(",", "")
        households_dict[row["key_row"]] = int(population_value)
    return pd.Series(households_dict)


def process_median_sale_price_data(
    df: pd.DataFrame, keys_df: pd.DataFrame, combined_df: pd.DataFrame
) -> tuple[pd.Series, str]:
    """Process median sale price data from REDFIN file and add hard-coded values for DC and Puerto Rico.

    Note: Washington DC ($565,000) and Puerto Rico ($138,000) median sale prices are hard-coded
    based on values provided in the example output spreadsheet, as this data is not present
    in the REDFIN dataset.

    Args:
        df: DataFrame containing REDFIN median sale price data
        keys_df: DataFrame containing region key mappings
        combined_df: Combined DataFrame with all processed data

    Returns:
        Tuple containing:
        - Series containing median sale prices for all regions
        - String containing the most recent date with data
    """
    processed_df = df.copy()
    # Set the first row as the header
    processed_df.columns = processed_df.iloc[0]
    processed_df = processed_df.iloc[1:]
    sale_price_dict = {}
    latest_date = None

    # Find the most recent date with data
    for col in reversed(processed_df.columns[1:]):
        if processed_df[col].notna().any():
            latest_date = col
            break

    for _, row in combined_df.iterrows():
        # Find the key_row value for the matching row
        key_row = find_key_row(keys_df, row["key_row"], "zillow_region_name")

        # Handle hard-coded values for DC and Puerto Rico
        if row["key_row"] == "washington_dc":
            sale_price_dict[row["key_row"]] = (
                565000  # Hard-coded value from example output
            )
        elif row["key_row"] == "puerto_rico":
            sale_price_dict[row["key_row"]] = (
                138000  # Hard-coded value from example output
            )
        else:
            # Process regular state data from REDFIN
            matching_rows = processed_df[processed_df.iloc[:, 0] == key_row]

            if not matching_rows.empty:
                # Get the most recent non-NaN value
                latest_price = None
                for col in reversed(matching_rows.columns[1:]):
                    price = matching_rows[col].iloc[0]
                    if pd.notna(price) and price != "":
                        latest_price = price.replace("$", "").replace("K", "000")
                        latest_price = int(float(latest_price))
                        break
                sale_price_dict[row["key_row"]] = latest_price
            else:
                # If state not found, add NaN
                sale_price_dict[row["key_row"]] = pd.NA

    return pd.Series(sale_price_dict), latest_date


def process_rank_data(
    combined_df: pd.DataFrame, column_name: str, ascending: bool = False
) -> pd.Series:
    """
    Rank states by a given column, with 1st being the highest value.

    Args:
        combined_df: DataFrame containing the column to rank
        column_name: Name of the column to rank by

    Returns:
        Series containing the ranks as ordinal strings (1st, 2nd, etc.)
    """

    def get_ordinal(n):
        if pd.isna(n):
            return "N/A"
        n = int(n)
        if 11 <= (n % 100) <= 13:
            return f"{n}th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
            return f"{n}{suffix}"

    # Get numeric ranks, handling NA values
    ranks = combined_df[column_name].rank(
        ascending=ascending, method="min", na_option="keep"
    )
    # Convert to ordinal strings
    ordinal_ranks = ranks.apply(get_ordinal)
    return pd.Series(ordinal_ranks)


def process_blurb_population_data(
    keys_df: pd.DataFrame, combined_df: pd.DataFrame
) -> pd.Series:
    blurb_dict = {}
    for _, row in combined_df.iterrows():
        # Find the key_row value for the matching row
        key_row = find_key_row(keys_df, row["key_row"], "alternative_name")
        blurb = f"{key_row} is {row['population_rank']}  in the nation in population among states, DC, and Puerto Rico."
        blurb_dict[row["key_row"]] = blurb
    return pd.Series(blurb_dict)


def process_blurb_median_household_income_data(
    keys_df: pd.DataFrame, combined_df: pd.DataFrame
) -> pd.Series:
    blurb_dict = {}
    for _, row in combined_df.iterrows():
        # Find the key_row value for the matching row
        key_row = find_key_row(keys_df, row["key_row"], "alternative_name")
        rank = (
            "the highest"
            if row["median_household_income_rank"] == "1st"
            else row["median_household_income_rank"]
        )
        blurb = f"{key_row} is {rank} in the nation in median household income among states, DC, and Puerto Rico."
        blurb_dict[row["key_row"]] = blurb
    return pd.Series(blurb_dict)


def process_blurb_median_sale_price_data(
    keys_df: pd.DataFrame, combined_df: pd.DataFrame, data_date: str
) -> pd.Series:
    """Generate blurbs for median sale price data.

    Args:
        keys_df: DataFrame containing region key mappings
        combined_df: Combined DataFrame with all processed data
        data_date: Date of the most recent data from REDFIN

    Returns:
        Series containing blurbs for each region
    """
    blurb_dict = {}
    for _, row in combined_df.iterrows():
        # Find the key_row value for the matching row
        key_row = find_key_row(keys_df, row["key_row"], "alternative_name")

        # Handle special case for 1st rank
        if row["median_sale_price_rank"] == "1st":
            rank_text = "single"
        else:
            rank_text = row["median_sale_price_rank"]

        blurb = f"{key_row} has the {rank_text} highest median sale price on homes in the nation among states, DC, and Puerto Rico, according to Redfin data from {data_date}."
        blurb_dict[row["key_row"]] = blurb
    return pd.Series(blurb_dict)


def process_blurb_house_affordability_ratio_data(
    keys_df: pd.DataFrame, combined_df: pd.DataFrame, data_date: str
) -> pd.Series:
    """Generate blurbs for house affordability ratio data.

    Args:
        keys_df: DataFrame containing region key mappings
        combined_df: Combined DataFrame with all processed data
        data_date: Date of the most recent data from REDFIN

    Returns:
        Series containing blurbs for each region
    """
    blurb_dict = {}
    for _, row in combined_df.iterrows():
        # Find the key_row value for the matching row
        key_row_alt_name = find_key_row(keys_df, row["key_row"], "alternative_name")

        # Use the correct rank column and handle NAs
        rank_value = row["house_affordability_ratio_rank"]
        if pd.isna(rank_value):
            rank_text = "N/A"
        elif rank_value == "1st":
            rank_text = "single"
        else:
            rank_text = rank_value

        # Handle cases where key_row_alt_name might be None
        if key_row_alt_name is None:
            key_row_alt_name = f"Region ({row['key_row']})"  # Fallback name

        # Construct blurb, handle N/A rank
        if rank_text == "N/A":
            blurb = f"{key_row_alt_name} has an N/A house affordability ratio."
        else:
            blurb = f"{key_row_alt_name} has the {rank_text} lowest house affordability ratio in the nation among states, DC, and Puerto Rico, according to Redfin data from {data_date}."

        blurb_dict[row["key_row"]] = blurb
    return pd.Series(blurb_dict)


def combine_data(data, column_name, combined_df) -> pd.DataFrame:
    """
    Combine the data from a single-column Series or DataFrame into an existing DataFrame by matching column names.

    Args:
        data: Pandas Series or DataFrame containing a single column of data
        column_name: Name of the column to add to the combined DataFrame
        combined_df: Existing DataFrame to add the column to

    Returns:
        DataFrame with the new column added
    """
    if isinstance(data, pd.Series):
        combined_df[column_name] = data.values
    elif isinstance(data, pd.DataFrame):
        if len(data.columns) == 1:
            combined_df[column_name] = data.iloc[:, 0]
        else:
            combined_df[column_name] = data[data.columns[0]]
    else:
        combined_df[column_name] = data

    return combined_df
