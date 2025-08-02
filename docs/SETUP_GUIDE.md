# Production Setup Guide

## Overview
This guide walks you through setting up the production-scale BlueDot Trading System for processing 1000+ JSON files automatically.

## 📋 Prerequisites

### Required Accounts
- ✅ **GitHub Account** (for automation and hosting)
- ✅ **Google Account** (for Google Drive storage)
- ✅ **TradingView Account** (for Pine Script integration)
- ✅ **Slack/Discord** (optional, for notifications)

### Required Skills
- Basic command line usage
- Basic Git operations
- Understanding of JSON/CSV formats

## 🔧 Step-by-Step Setup

### 1. Repository Setup

#### Fork the Repository
```bash
# 1. Go to GitHub and fork this repository
# 2. Clone your fork locally
git clone https://github.com/YOUR_USERNAME/bluedot-trading-system.git
cd bluedot-trading-system

# 3. Enable GitHub Actions in your repository settings
# 4. Enable GitHub Pages (Settings → Pages → Source: GitHub Actions)
```

### 2. Google Drive Setup

#### Create Folder Structure
```
📁 BlueDot-Trading-Data/
├── 📅 daily/
│   ├── 2024-08-01/
│   │   ├── AAPL_daily.json
│   │   ├── MSFT_daily.json
│   │   └── ... (1000+ JSON files)
│   ├── 2024-08-02/
│   └── latest/ → 2024-08-02/
├── 📊 weekly/
│   ├── 2024-W31/
│   │   ├── AAPL_weekly.json
│   │   ├── MSFT_weekly.json
│   │   └── ... (1000+ JSON files)
│   └── latest/ → 2024-W31/
└── 🔄 triggers/
    ├── daily_ready.txt      # Contains: "2024-08-02"
    ├── weekly_ready.txt     # Contains: "2024-W31"
    └── status_log.txt
```

#### Get Google Drive API Key
```bash
# 1. Go to Google Cloud Console
# 2. Enable Google Drive API
# 3. Create credentials (API Key)
# 4. Note down your API key
```

#### Get Folder IDs
```bash
# 1. Open your Google Drive folder in browser
# 2. Copy the folder ID from URL:
#    https://drive.google.com/drive/folders/[FOLDER_ID_HERE]
# 3. Note down folder IDs for daily and weekly folders
```

### 3. GitHub Secrets Configuration

#### Required Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

```bash
# Google Drive Integration
GOOGLE_DRIVE_API_KEY          # Your Google Drive API key
DAILY_FOLDER_ID               # Google Drive folder ID for daily data
WEEKLY_FOLDER_ID              # Google Drive folder ID for weekly data

# Notifications (Optional)
SUCCESS_WEBHOOK_URL           # Slack/Discord webhook for success notifications
ERROR_WEBHOOK_URL             # Slack/Discord webhook for error notifications

# TradingView (Optional)
TRADINGVIEW_NAMESPACE         # Your TradingView namespace for seed data
```

#### Setting Up Webhook Notifications (Optional)

**For Slack:**
```bash
# 1. Go to your Slack workspace
# 2. Create new app: https://api.slack.com/apps
# 3. Enable "Incoming Webhooks"
# 4. Add webhook to workspace
# 5. Copy webhook URL to GitHub secrets
```

**For Discord:**
```bash
# 1. Go to your Discord server
# 2. Server Settings → Integrations → Webhooks
# 3. Create New Webhook
# 4. Copy webhook URL to GitHub secrets
```

### 4. Testing the Setup

#### Test with Sample Data
```bash
# 1. Upload sample JSONs to Google Drive test folder
# 2. Trigger GitHub Action manually:
#    GitHub Repository → Actions → Daily Data Pipeline → Run workflow

# 3. Check the logs for processing status
# 4. Verify CSV files are generated in GitHub Pages
```

#### Verify GitHub Pages Output
```bash
# Check if your CSVs are accessible at:
# https://YOUR_USERNAME.github.io/bluedot-trading-system/daily/latest/AAPL_BLUE_DOTS.csv
```

## 📊 Daily Operations Workflow

### Morning Routine (Automated)
```bash
# 1. Upload your 1000+ JSON files to Google Drive:
#    📁 BlueDot-Data/daily/2024-08-02/
#    
# 2. Create trigger file:
#    📄 triggers/daily_ready.txt → "2024-08-02"
#    
# 3. GitHub Actions automatically detects and processes
# 4. Receive Slack/Discord notification when complete
# 5. Use processed data in TradingView immediately
```

### Weekly Routine (Automated)
```bash
# 1. Upload weekly JSON files to:
#    📁 BlueDot-Data/weekly/2024-W31/
#    
# 2. Create trigger file:
#    📄 triggers/weekly_ready.txt → "2024-W31"
#    
# 3. Weekly processing runs every Sunday automatically
```

## 🎯 TradingView Integration

### Upload CSV as Seed Data
```bash
# 1. Go to TradingView → Chart → Indicators
# 2. Pine Editor → Create new script
# 3. Use request.seed() to access your data:

blue_dot = request.seed('your_namespace', 'AAPL_BLUE_DOTS', close)
```

### Pine Script Template
```pine
//@version=5
strategy("BlueDot Automated Strategy", overlay=true)

// Input for stock selection
symbol_input = input.string("AAPL", "Stock Symbol")
timeframe_input = input.string("daily", "Timeframe", options=["daily", "weekly"])

// Dynamic data access
namespace = "yourusername_bluedot_" + timeframe_input + "_" + symbol_input
blue_dot = request.seed(namespace, 'BLUE_DOTS', close)
rlst = request.seed(namespace, 'RLST_RATING', close)
bc = request.seed(namespace, 'BC_INDICATOR', close)

// Strategy logic
buy_signal = blue_dot == 1 and rlst > 80 and bc > 25000
sell_signal = rlst < 30 or bc < bc[5]

if buy_signal
    strategy.entry("Long", strategy.long)
if sell_signal
    strategy.close("Long")
```

## 🔍 Monitoring & Troubleshooting

### Check Processing Status
```bash
# 1. GitHub Repository → Actions → View workflow runs
# 2. Check processing logs for errors
# 3. Verify notification delivery
# 4. Check GitHub Pages deployment
```

### Common Issues

#### "No files found"
```bash
# Check:
# 1. Google Drive folder structure is correct
# 2. API key has proper permissions
# 3. Folder IDs are correct in GitHub secrets
```

#### "Processing failed"
```bash
# Check:
# 1. JSON file format matches expected structure
# 2. All required fields (rlst, bc, blueDotData) are present
# 3. GitHub Actions runtime limits (6 hours max)
```

#### "TradingView can't access data"
```bash
# Check:
# 1. GitHub Pages is enabled and deployed
# 2. CSV files are in correct format
# 3. request.seed() namespace is correct
```

### Performance Optimization

#### For Large Datasets (2000+ files)
```bash
# 1. Split into multiple batches
# 2. Increase parallel workers in config
# 3. Consider multiple repositories for different timeframes
```

#### Storage Management
```bash
# 1. Monitor GitHub repository size (2GB limit)
# 2. Archive old data periodically
# 3. Use compression for large CSV files
```

## 🚨 Backup & Recovery

### Data Backup Strategy
```bash
# 1. Keep original JSONs in Google Drive (permanent storage)
# 2. GitHub provides version control for processed CSVs
# 3. Export critical data periodically for offline backup
```

### Disaster Recovery
```bash
# 1. Fork/clone repository to new account if needed
# 2. Re-upload JSONs to new Google Drive folder
# 3. Update GitHub secrets with new credentials
# 4. Trigger fresh processing run
```

## 📈 Scaling Considerations

### Current Limits
- **GitHub Actions**: 2000 minutes/month free, 6 hours per run
- **GitHub Storage**: 2GB per repository
- **GitHub Pages**: 100GB bandwidth/month
- **Google Drive API**: 1 billion requests/day free

### Scaling Options
1. **Multiple Repositories**: Split by timeframe or market
2. **Cloud Functions**: For unlimited processing time
3. **Self-Hosted Runners**: For custom hardware requirements
4. **CDN Integration**: For faster CSV access globally

## 🎓 Advanced Configuration

### Custom Processing Rules
```yaml
# Edit config/data_config.yaml
batch_processing:
  max_files_per_batch: 200      # Increase for more files per batch
  parallel_workers: 8           # More workers for faster processing
  
signals:
  bc_indicator:
    typical_range: [20000, 30000]  # Adjust based on your data
```

### Custom Notifications
```python
# Edit src/monitoring/notification_system.py
# Add custom notification channels
# Customize message formats
# Add health monitoring alerts
```

---

**Next Steps:**
1. Complete this setup guide
2. Test with small dataset first
3. Scale up to full 1000+ files
4. Integrate with your trading strategies
5. Monitor and optimize performance