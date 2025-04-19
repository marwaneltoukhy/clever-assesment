"""
Time series analysis of Redfin median sale price data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from rich.console import Console
from rich.table import Table

console = Console()


def load_redfin_data(file_path: Path) -> pd.DataFrame:
    """
    Load and preprocess Redfin median sale price data.

    Args:
        file_path: Path to the Redfin data CSV file

    Returns:
        DataFrame with time series data for each state
    """
    df = pd.read_csv(file_path)
    
    # Set the first row as header
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    
    # Set Region as index
    df.set_index('Region', inplace=True)
    
    # Convert price strings to numeric values
    for col in df.columns:
        df[col] = pd.to_numeric(df[col].str.replace('$', '').str.replace('K', '000'), errors='coerce')
    
    # Convert columns to datetime with Month YYYY format
    df.columns = pd.to_datetime(df.columns, format='%B %Y')
    
    return df


def calculate_growth_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate year-over-year and month-over-month growth rates.

    Args:
        df: DataFrame with time series data

    Returns:
        DataFrame with growth rates
    """
    # Create a copy of the DataFrame to avoid fragmentation
    df_copy = df.copy()
    
    # Calculate growth rates using vectorized operations
    mom_growth = df_copy.pct_change(axis=1, fill_method=None) * 100
    yoy_growth = df_copy.pct_change(periods=12, axis=1, fill_method=None) * 100
    
    # Combine results into a single DataFrame
    return pd.concat([
        mom_growth.iloc[:, -1].rename('mom_growth'),
        yoy_growth.iloc[:, -1].rename('yoy_growth')
    ], axis=1)


def plot_all_states(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Create a single plot showing all states' time series with visual hierarchy.

    Args:
        df: DataFrame with time series data
        output_dir: Directory to save plots
    """
    # Get latest prices for sorting
    latest_prices = df.iloc[:, -1]
    
    # Identify top and bottom states by latest price
    top_5_states = latest_prices.nlargest(5).index
    bottom_5_states = latest_prices.nsmallest(5).index
    highlighted_states = set(top_5_states) | set(bottom_5_states)
    
    # Create figure
    plt.figure(figsize=(20, 10))
    
    # Plot background states first (gray, thin lines)
    for state in df.index:
        if state not in highlighted_states:
            state_data = df.loc[state].dropna()
            plt.plot(state_data.index, state_data.values, 
                    color='gray', alpha=0.2, linewidth=1)
    
    # Plot highlighted states with distinct colors
    colors = plt.cm.Set2(np.linspace(0, 1, len(highlighted_states)))
    for state, color in zip(highlighted_states, colors):
        state_data = df.loc[state].dropna()
        plt.plot(state_data.index, state_data.values,
                label=f"{state} (${state_data.iloc[-1]:,.0f})",
                color=color, linewidth=2.5)
    
    # Customize the plot
    plt.title('Median Sale Price Trends\nTop 5 and Bottom 5 States Highlighted', 
              fontsize=14, pad=20)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price ($)', fontsize=12)
    
    # Add grid with custom style
    plt.grid(True, linestyle='--', alpha=0.3)
    
    # Format y-axis to show thousands with K
    plt.gca().yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f'${x/1000:,.0f}K'))
    
    # Customize ticks
    plt.xticks(rotation=45, ha='right')
    plt.tick_params(axis='both', which='major', labelsize=10)
    
    # Add legend only for highlighted states
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
              fontsize=10, framealpha=1)
    
    # Add a light gray background grid
    plt.gca().set_facecolor('#f8f9fa')
    plt.grid(True, linestyle='--', alpha=0.3, color='white')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_dir / 'median_sale_price_trends.png',
                bbox_inches='tight', dpi=300,
                facecolor='#f8f9fa')
    plt.close()


def plot_summary_stats(summary_df: pd.DataFrame, output_dir: Path) -> None:
    """
    Create visualizations of the summary statistics.

    Args:
        summary_df: DataFrame with summary statistics
        output_dir: Directory to save plots
    """
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # Plot 1: Latest prices
    summary_df = summary_df.sort_values('latest_price', ascending=False)
    sns.barplot(data=summary_df, x='state', y='latest_price', ax=ax1)
    ax1.set_title('Latest Median Sale Price by State')
    ax1.set_xlabel('State')
    ax1.set_ylabel('Price ($)')
    ax1.tick_params(axis='x', rotation=90)
    
    # Plot 2: Growth rates
    summary_df = summary_df.sort_values('yoy_growth', ascending=False)
    sns.barplot(data=summary_df, x='state', y='yoy_growth', ax=ax2)
    ax2.set_title('Year-over-Year Growth Rate by State')
    ax2.set_xlabel('State')
    ax2.set_ylabel('Growth Rate (%)')
    ax2.tick_params(axis='x', rotation=90)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_dir / 'price_and_growth_summary.png',
                bbox_inches='tight', dpi=300)
    plt.close()


def display_summary_stats(df: pd.DataFrame) -> None:
    """
    Display summary statistics for the time series data.

    Args:
        df: DataFrame with time series data
    """
    table = Table(title="Time Series Summary Statistics")
    table.add_column("Statistic", style="cyan")
    table.add_column("Value", justify="right", style="green")
    
    # Calculate statistics
    start_date = df.columns[0]
    end_date = df.columns[-1]
    num_states = len(df)
    latest_data = df.iloc[:, -1].dropna()
    avg_price = latest_data.mean()
    max_price = latest_data.max()
    min_price = latest_data.min()
    
    table.add_row("Time Period", f"{start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')}")
    table.add_row("Number of States", str(num_states))
    table.add_row("Average Price (Latest)", f"${avg_price:,.0f}")
    table.add_row("Maximum Price (Latest)", f"${max_price:,.0f}")
    table.add_row("Minimum Price (Latest)", f"${min_price:,.0f}")
    
    console.print()
    console.print(table)


def analyze_time_series(input_dir: Path, output_dir: Path) -> None:
    """
    Main function to perform time series analysis on Redfin data.

    Args:
        input_dir: Directory containing input files
        output_dir: Directory to save output files
    """
    # Load data
    redfin_file = input_dir / "REDFIN_MEDIAN_SALE_PRICE.csv"
    df = load_redfin_data(redfin_file)
    
    # Display summary statistics
    display_summary_stats(df)
    
    # Calculate growth rates
    growth_rates = calculate_growth_rates(df)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create combined results DataFrame
    results = pd.DataFrame({
        'state': df.index,
        'latest_price': df.iloc[:, -1],
        'mom_growth': growth_rates['mom_growth'],
        'yoy_growth': growth_rates['yoy_growth']
    })
    
    # Save combined results to a single CSV
    results.to_csv(output_dir / 'median_sale_price_analysis.csv', index=False)
    
    # Create visualizations
    plot_all_states(df, output_dir)
    plot_summary_stats(results, output_dir)
    
    console.print(f"\nAnalysis complete! Results saved to {output_dir}") 