# BlueDot Trading System Data

This directory contains processed CSV files for TradingView integration.

## Directory Structure

- `daily/` - Daily processed data files
- `weekly/` - Weekly processed data files

## File Naming Convention

Each stock generates 4 CSV files:
- `{SYMBOL}_PRICE_DATA.csv` - OHLCV price data
- `{SYMBOL}_RLST_RATING.csv` - Relative strength ratings
- `{SYMBOL}_BC_INDICATOR.csv` - Base count indicators
- `{SYMBOL}_BLUE_DOTS.csv` - Trading signals

## Data Format

All CSV files follow TradingView's expected format:
```
timestamp,open,high,low,close,volume
20240802T1430,100.50,101.00,100.25,100.75,1000000
```

## Access in TradingView

Use the `request.seed()` function in Pine Script:
```pine
blue_dots = request.seed('stocks_chimmu_ms_daily_AAPL', 'BLUE_DOTS', close)
```