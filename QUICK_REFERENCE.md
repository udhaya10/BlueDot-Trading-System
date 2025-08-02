# BlueDot Trading System - Quick Reference

## 🔑 Critical IDs & Configurations

### Google Drive
```
Daily Folder:  1-L9PF0zZqtalEHdVPkHLeGDAyuvN5MUo
Weekly Folder: 1-LY72Ml_FXr5SJK8wCySlSMB78OU6gM4
Service Email: trading-rag-service@tradingviewdatapipeline.iam.gserviceaccount.com
```

### GitHub & TradingView
```
GitHub User:    udhaya10
TradingView NS: stocks_chimmu_ms
GitHub Pages:   https://udhaya10.github.io/BlueDot-Trading-System
```

## 🚀 Essential Commands

```bash
# Activate environment
source venv/bin/activate

# Test connection
python test_google_drive.py

# Process daily data (example: Aug 2, 2024)
python src/batch_processing/batch_processor.py --timeframe daily --date 2024-08-02

# Process weekly data (example: Week 31, 2024)
python src/batch_processing/batch_processor.py --timeframe weekly --date 2024-W31
```

## 📁 Key File Locations

```
.credentials/google-drive-service-account.json  # Service account
.env                                           # Environment config
test_google_drive.py                          # Connection test
src/batch_processing/batch_processor.py       # Main processor
```

## 📊 TradingView Pine Script Template

```pine
//@version=5
indicator("BlueDot Trading Signals", overlay=true)

// Access your data
symbol = "AAPL"
blue_dots = request.seed('stocks_chimmu_ms_daily_' + symbol, 'BLUE_DOTS', close)
rlst = request.seed('stocks_chimmu_ms_daily_' + symbol, 'RLST_RATING', close)
bc = request.seed('stocks_chimmu_ms_daily_' + symbol, 'BC_INDICATOR', close)

// Plot signals
plotshape(blue_dots == 1, "Blue Dot", shape.circle, location.belowbar, color.blue, size=size.small)
```

## ⚡ Processing Workflow

1. **Upload JSON files** → Google Drive (daily/weekly folders)
2. **Run processor** → `python src/batch_processing/batch_processor.py`
3. **Access in TradingView** → Use namespace: `stocks_chimmu_ms`

---
Save this file for quick reference during development!