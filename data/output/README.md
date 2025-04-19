# Time Series Analysis Outputs

This directory contains the outputs from the Redfin median sale price time series analysis.

## Files

### 1. median_sale_price_analysis.csv

A comprehensive CSV file containing analysis results for all states:

- `state`: Name of the state
- `latest_price`: Most recent median sale price
- `mom_growth`: Month-over-month growth rate (percentage)
- `yoy_growth`: Year-over-year growth rate (percentage)

### 2. median_sale_price_trends.png

A visualization showing median sale price trends for all states from 2012 to 2025:

- Gray lines: Background trends for all states
- Colored lines: Top 5 and bottom 5 states by latest price
- Legend: Shows state names with their latest prices
- Y-axis: Prices in thousands ($K)
- X-axis: Timeline from 2012 to 2025

### 3. price_and_growth_summary.png

Two bar charts showing:

1. Latest Median Sale Price by State
   - Sorted from highest to lowest price
   - Shows the current market position of each state

2. Year-over-Year Growth Rate by State
   - Sorted from highest to lowest growth rate
   - Shows which states are experiencing the fastest price growth

## Analysis Details

- Time Period: January 2012 to February 2025
- Number of States: 51 (including District of Columbia)
- Data Source: Redfin median sale price data
- Update Frequency: Monthly

## Key Statistics

- Average Price (Latest): $400,078
- Maximum Price (Latest): $833,000
- Minimum Price (Latest): $228,000

## Notes

- All prices are in USD
- Growth rates are calculated as percentage changes
- Missing values are excluded from calculations
- States with insufficient data points may show gaps in the time series 