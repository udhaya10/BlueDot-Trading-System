# Production Deployment Guide

## Overview
Complete guide for deploying the production-scale BlueDot Trading System that processes 1000+ JSON files automatically. From zero to trading in 30 minutes.

## 🎯 **Deployment Overview**

### What You'll Build
- **Automated Pipeline**: 1000+ JSONs → 4000+ CSVs → TradingView (zero manual work)
- **Cloud Infrastructure**: GitHub Actions + Google Drive + GitHub Pages
- **Monitoring**: Slack/Discord notifications + health monitoring
- **Trading Integration**: Immediate Pine Script access to processed data

### Prerequisites Checklist
- [ ] GitHub account (free)
- [ ] Google account with Drive access (free)
- [ ] TradingView account (free/paid)
- [ ] Slack/Discord (optional, for notifications)
- [ ] Basic command line knowledge

## 📋 **Phase 1: Repository Setup (5 minutes)**

### Step 1: Fork and Configure Repository
```bash
# 1. Go to GitHub and fork this repository
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/bluedot-trading-system.git
cd bluedot-trading-system

# 3. Enable GitHub Actions
# Repository → Settings → Actions → General → Allow all actions

# 4. Enable GitHub Pages  
# Repository → Settings → Pages → Source: GitHub Actions
```

### Step 2: Verify Repository Structure
```bash
# Ensure all production files are present
ls -la .github/workflows/  # Should see daily-pipeline.yml, weekly-pipeline.yml
ls -la src/batch_processing/  # Should see batch_processor.py
ls -la src/cloud_integration/  # Should see google_drive_client.py
ls -la src/monitoring/  # Should see notification_system.py
```

## 🔧 **Phase 2: Google Drive Integration (10 minutes)**

### Step 1: Create Folder Structure
Create this exact structure in your Google Drive:
```
📁 BlueDot-Trading-Data/
├── 📅 daily/
│   ├── 2024-08-01/          # Example date folder
│   ├── 2024-08-02/          # Today's date
│   │   ├── AAPL_daily.json  # Individual stock files
│   │   ├── MSFT_daily.json
│   │   ├── GOOGL_daily.json
│   │   └── ... (place your 1000+ JSON files here)
│   └── latest/              # Will be updated automatically
├── 📊 weekly/
│   ├── 2024-W31/            # Example week folder
│   ├── 2024-W32/            # Current week
│   │   ├── AAPL_weekly.json
│   │   ├── MSFT_weekly.json
│   │   └── ... (place your 1000+ JSON files here)  
│   └── latest/
└── 🔄 triggers/
    ├── daily_ready.txt      # Contains: "2024-08-02"
    ├── weekly_ready.txt     # Contains: "2024-W32"
    └── processing_log.txt   # Auto-generated status
```

### Step 2: Get Google Drive API Credentials
```bash
# 1. Go to Google Cloud Console: https://console.cloud.google.com
# 2. Create new project or select existing
# 3. Enable Google Drive API:
#    APIs & Services → Library → Search "Google Drive API" → Enable
# 4. Create credentials:
#    APIs & Services → Credentials → Create Credentials → API Key
# 5. Copy your API key (looks like: AIzaSyD...)
```

### Step 3: Get Folder IDs
```bash
# 1. Open your Google Drive folders in browser
# 2. Copy folder IDs from URLs:

# Daily folder: https://drive.google.com/drive/folders/1ABC...XYZ
# Copy: 1ABC...XYZ

# Weekly folder: https://drive.google.com/drive/folders/1DEF...UVW  
# Copy: 1DEF...UVW

# Main folder: https://drive.google.com/drive/folders/1GHI...RST
# Copy: 1GHI...RST
```

## 🔐 **Phase 3: GitHub Secrets Configuration (5 minutes)**

### Required Secrets
Go to: Repository → Settings → Secrets and variables → Actions → New repository secret

```bash
# Google Drive Integration (Required)
GOOGLE_DRIVE_API_KEY          # Your API key from Step 2
DAILY_FOLDER_ID               # Daily folder ID from Step 3
WEEKLY_FOLDER_ID              # Weekly folder ID from Step 3

# Notifications (Optional but Recommended)
SUCCESS_WEBHOOK_URL           # Slack/Discord webhook for success
ERROR_WEBHOOK_URL             # Slack/Discord webhook for errors

# TradingView (Optional)
TRADINGVIEW_NAMESPACE         # Your namespace for seed data
```

### Setting Up Slack Notifications (Optional)
```bash
# 1. Go to your Slack workspace
# 2. Create app: https://api.slack.com/apps → Create New App
# 3. Features → Incoming Webhooks → Activate → Add New Webhook
# 4. Select channel → Copy webhook URL
# 5. Add to GitHub secrets as SUCCESS_WEBHOOK_URL
```

### Setting Up Discord Notifications (Optional)
```bash
# 1. Go to your Discord server
# 2. Server Settings → Integrations → Webhooks → New Webhook
# 3. Choose channel → Copy webhook URL  
# 4. Add to GitHub secrets as SUCCESS_WEBHOOK_URL
```

## 🧪 **Phase 4: Testing (5 minutes)**

### Step 1: Upload Test Data
```bash
# 1. Upload 3-5 sample JSON files to:
#    Google Drive/BlueDot-Trading-Data/daily/2024-08-02/

# 2. Create trigger file:
#    Create: triggers/daily_ready.txt
#    Content: "2024-08-02"
```

### Step 2: Manual Trigger Test
```bash
# 1. Go to GitHub Repository → Actions
# 2. Select "Daily Data Pipeline"
# 3. Click "Run workflow" → Use workflow from main → Run workflow
# 4. Watch the logs for processing status
```

### Step 3: Verify Output
```bash
# After successful run, check:
# 1. Repository → docs/ folder should have new CSV files
# 2. GitHub Pages should be deployed: 
#    https://YOUR_USERNAME.github.io/bluedot-trading-system/

# 3. Check CSV access:
#    https://YOUR_USERNAME.github.io/bluedot-trading-system/daily/2024-08-02/AAPL_BLUE_DOTS.csv
```

## 🚀 **Phase 5: Production Launch (5 minutes)**

### Step 1: Upload Full Dataset
```bash
# Upload your 1000+ JSON files to appropriate folders:
# Daily: BlueDot-Trading-Data/daily/YYYY-MM-DD/
# Weekly: BlueDot-Trading-Data/weekly/YYYY-WXX/
```

### Step 2: Set Up Automatic Scheduling
```bash
# Workflows are already configured for:
# - Daily processing: 9 AM UTC every day
# - Weekly processing: 10 AM UTC every Sunday

# To change schedule, edit:
# .github/workflows/daily-pipeline.yml (line with 'cron:')
# .github/workflows/weekly-pipeline.yml (line with 'cron:')
```

### Step 3: TradingView Integration
```pine
//@version=5
strategy("BlueDot Production Strategy", overlay=true)

// Your processed data is automatically available:
symbol_input = input.string("AAPL", "Stock Symbol")
timeframe_input = input.string("daily", "Timeframe", options=["daily", "weekly"])

// Dynamic data access (auto-updated daily)
namespace = "yourusername_bluedot_" + timeframe_input + "_" + symbol_input
blue_dot = request.seed(namespace, 'BLUE_DOTS', close)
rlst = request.seed(namespace, 'RLST_RATING', close)
bc = request.seed(namespace, 'BC_INDICATOR', close)

// Your trading logic here
buy_signal = blue_dot == 1 and rlst > 80 and bc > 25000
```

## 📊 **Daily Operations Workflow**

### Morning Routine (5 minutes)
```bash
# 1. Upload 1000+ JSON files to Google Drive:
#    daily/YYYY-MM-DD/ or weekly/YYYY-WXX/

# 2. Update trigger file:
#    triggers/daily_ready.txt → "YYYY-MM-DD"
#    triggers/weekly_ready.txt → "YYYY-WXX"

# 3. ☕ Coffee time - everything else is automated
```

### Automated Processing (45-60 minutes)
```bash
# GitHub Actions automatically:
# 1. Detects trigger file (9 AM daily, 10 AM Sunday)
# 2. Downloads 1000+ JSONs from Google Drive
# 3. Processes in parallel batches (4 workers)
# 4. Generates 4000+ CSV files
# 5. Deploys to GitHub Pages
# 6. Sends Slack/Discord notification
```

### Trading (Immediate)
```bash
# Your data is immediately available in TradingView:
# - 1000+ stocks processed
# - 4 data types per stock (PRICE, RLST, BC, BLUE_DOTS)
# - Fresh signals ready for Pine Script strategies
```

## 🔍 **Monitoring & Troubleshooting**

### Check Processing Status
```bash
# 1. GitHub Repository → Actions → View latest workflow run
# 2. Check Slack/Discord notifications
# 3. Visit status dashboard:
#    https://YOUR_USERNAME.github.io/bluedot-trading-system/
```

### Common Issues & Solutions

#### "No files found in Google Drive"
```bash
# Check:
# 1. Folder structure matches exactly as shown above
# 2. API key has Google Drive API enabled
# 3. Folder IDs are correct in GitHub secrets
# 4. Files are in correct date/week folders
```

#### "Processing failed"
```bash
# Check:
# 1. JSON files match expected structure
# 2. All required fields present (rlst, bc, blueDotData)
# 3. File naming convention: SYMBOL_timeframe.json
# 4. Processing time under GitHub Actions 6-hour limit
```

#### "TradingView can't access data"
```bash
# Check:
# 1. GitHub Pages is enabled and deployed
# 2. CSV files are in docs/ folder
# 3. request.seed() namespace matches your setup
# 4. File naming convention in TradingView matches output
```

### Performance Optimization

#### For 2000+ Files
```bash
# 1. Edit config/data_config.yaml:
#    max_files_per_batch: 50  # Reduce batch size
#    parallel_workers: 6      # Increase workers

# 2. Consider splitting into multiple repositories
# 3. Use weekly processing for larger datasets
```

#### Speed Improvements
```bash
# 1. Optimize JSON file sizes (remove unnecessary data)
# 2. Use compression for large CSV outputs
# 3. Process only changed files (delta processing)
# 4. Archive old data periodically
```

## 🚨 **Production Maintenance**

### Weekly Tasks
- [ ] Monitor processing success rates
- [ ] Check storage usage (GitHub 2GB limit)
- [ ] Verify data quality and completeness
- [ ] Update trigger files for weekly processing

### Monthly Tasks  
- [ ] Archive old processed data
- [ ] Review performance metrics
- [ ] Update API keys if needed
- [ ] Optimize processing parameters

### Emergency Procedures
```bash
# If processing fails:
# 1. Check GitHub Actions logs for errors
# 2. Verify Google Drive folder structure
# 3. Re-run workflow manually
# 4. Contact support with error logs

# If data is corrupted:
# 1. Re-upload original JSON files
# 2. Trigger fresh processing
# 3. Verify output CSV integrity
# 4. Update TradingView strategies if needed
```

## 📈 **Scaling Options**

### Current Limits
- **GitHub Actions**: 2000 minutes/month (free), 6 hours per run
- **GitHub Storage**: 2GB per repository  
- **GitHub Pages**: 100GB bandwidth/month
- **Google Drive**: 15GB storage (free), 1B API requests/day

### Scaling Strategies
1. **Multiple Repositories**: Split by market/timeframe
2. **Paid GitHub**: Increase limits with GitHub Pro/Team
3. **Cloud Functions**: Unlimited processing time
4. **Self-hosted**: Custom infrastructure for massive scale

---

## 🎯 **Deployment Complete!**

Your production BlueDot Trading System is now live and processing 1000+ stocks automatically. Upload JSONs in the morning, trade with fresh signals by market open.

**Support**: Check [troubleshooting docs](TROUBLESHOOTING.md) or create GitHub issue for help.