# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Development Commands

### Environment Setup
```bash
# Initial setup
./scripts/setup.sh
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup pre-commit hooks
pre-commit install
```

### Core Processing Commands
```bash
# Process daily batch (primary workflow)
python src/batch_processing/batch_processor.py --timeframe daily --date 2024-08-02

# Process weekly batch
python src/batch_processing/batch_processor.py --timeframe weekly --date 2024-W31

# Validate data integrity
python src/batch_processing/validate_batch_data.py --timeframe daily
```

### Testing and Quality
```bash
# Run full test suite
pytest tests/ -v --cov

# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Pre-commit checks (runs black + flake8)
pre-commit run --all-files
```

## High-Level Architecture

### Production-Scale Data Pipeline
This is an **automated trading system** that processes 1000+ JSON files daily/weekly with zero manual intervention. The system follows this flow:

```
Google Drive (1000+ JSONs) → GitHub Actions → Batch Processing → GitHub Pages → TradingView
```

### Core Data Transformation
Each JSON file contains:
- **chart.prices**: OHLCV data with timestamps, RLST ratings (0-99), and BC indicators
- **blueDotData.dates**: Strategic trading signal dates
- **peripheralData**: Stock metadata and RS ratings

The system generates **4 CSV files per stock**:
1. `SYMBOL_PRICE_DATA.csv` - Standard OHLCV for price charts
2. `SYMBOL_RLST_RATING.csv` - Time-aligned relative strength ratings (0-99)
3. `SYMBOL_BC_INDICATOR.csv` - Time-aligned base count consolidation strength
4. `SYMBOL_BLUE_DOTS.csv` - Binary trading signals (1=signal, 0=no signal)

### Scalable Processing Architecture
- **Batch Processing**: `src/batch_processing/batch_processor.py` handles 1000+ files using parallel workers
- **Cloud Integration**: `src/cloud_integration/` manages Google Drive downloads and GitHub Pages uploads  
- **Configuration**: `config/data_config.yaml` defines production scaling (100 files/batch, 4 workers)
- **Automation**: `.github/workflows/` contains daily/weekly processing pipelines

### Key Production Settings
- **Batch Size**: 100 files per batch (configurable for 2000+ files)
- **Parallel Workers**: 4 concurrent processors (GitHub Actions optimized)
- **Processing Capacity**: 1000+ JSON → 4000+ CSV files in ~45 minutes
- **Output Format**: TradingView-compatible CSV with proper timestamps

### Data Validation Pipeline
The system validates:
- JSON structure completeness (`chart.prices`, `blueDotData`, `peripheralData`)
- Required fields in price data (`priceDate`, `open`, `high`, `low`, `close`, `volume`, `rlst`, `bc`)
- Data quality thresholds (max 10% missing data, min 30 data points)
- Chronological ordering of timestamps

### TradingView Integration
Processed CSVs are automatically deployed to GitHub Pages for TradingView seed data access:
```pine
// Access processed data in Pine Script
blue_dot = request.seed('username_bluedot_daily_AAPL', 'BLUE_DOTS', close)
rlst = request.seed('username_bluedot_daily_AAPL', 'RLST_RATING', close)
```

## Important Implementation Notes

### Data Processing Flow
1. **Input Validation**: Always validate JSON structure before processing
2. **Timestamp Conversion**: Convert millisecond timestamps to TradingView format (`YYYYMMDDTHHMM`)
3. **Signal Alignment**: Ensure RLST, BC, and BlueDot signals are time-aligned with price data
4. **Output Structure**: Maintain 6-column CSV format (timestamp, open, high, low, close, volume)

### Configuration Management
- **Production Config**: `config/data_config.yaml` contains all processing parameters
- **Scaling Options**: Multiple processing modes (standard, high_volume, memory_constrained)
- **Environment Variables**: Use `.env` for local development secrets

### Error Handling
- **Batch Processing**: Individual file failures don't stop the entire batch
- **Retry Logic**: 3 retry attempts for failed downloads/uploads
- **Notifications**: Slack/Discord alerts for processing status
- **Logging**: Comprehensive logging to `logs/data_processing.log`

### GitHub Actions Integration  
- **Daily Pipeline**: Runs at 9 AM UTC (`daily-pipeline.yml`)
- **Weekly Pipeline**: Runs Sunday 10 AM UTC (`weekly-pipeline.yml`)
- **Manual Triggers**: Support `workflow_dispatch` and `repository_dispatch`
- **Timeout**: 5-hour maximum processing time per workflow