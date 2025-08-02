# BlueDot Trading System - Configuration Summary

**Last Updated**: August 2, 2025  
**Status**: ✅ Configured and Tested

## 🔐 Service Account Configuration

### Service Account Details
- **Email**: `trading-rag-service@tradingviewdatapipeline.iam.gserviceaccount.com`
- **Credentials File**: `/Users/udhaya10/workspace/BlueDot-Trading-System/.credentials/google-drive-service-account.json`
- **Permissions**: Read-only access to Google Drive folders

### Security Setup
- Credentials directory permissions: `700` (owner read/write/execute only)
- Service account JSON permissions: `600` (owner read/write only)
- Added to `.gitignore` to prevent accidental commits

## 📁 Google Drive Configuration

### Folder IDs
- **Daily Data Folder ID**: `1-L9PF0zZqtalEHdVPkHLeGDAyuvN5MUo`
  - Folder Name: `daily`
  - URL: https://drive.google.com/drive/folders/1-L9PF0zZqtalEHdVPkHLeGDAyuvN5MUo
  
- **Weekly Data Folder ID**: `1-LY72Ml_FXr5SJK8wCySlSMB78OU6gM4`
  - Folder Name: `weekly`
  - URL: https://drive.google.com/drive/folders/1-LY72Ml_FXr5SJK8wCySlSMB78OU6gM4

### Access Configuration
Both folders are shared with the service account email with "Viewer" permissions.

## 🌐 GitHub Configuration

- **GitHub Username**: `udhaya10`
- **GitHub Repository**: `BlueDot-Trading-System`
- **GitHub Pages URL**: `https://udhaya10.github.io/BlueDot-Trading-System`

## 📊 TradingView Configuration

- **TradingView Namespace**: `stocks_chimmu_ms`

### Pine Script Usage Example
```pine
// Accessing processed data in TradingView
blue_dots = request.seed('stocks_chimmu_ms_daily_AAPL', 'BLUE_DOTS', close)
rlst_rating = request.seed('stocks_chimmu_ms_daily_AAPL', 'RLST_RATING', close)
bc_indicator = request.seed('stocks_chimmu_ms_daily_AAPL', 'BC_INDICATOR', close)
```

## 🔧 Environment Configuration

### Environment File Location
- **Path**: `/Users/udhaya10/workspace/BlueDot-Trading-System/.env`

### Current Settings
```env
# Google Drive Service Account Credentials
GOOGLE_DRIVE_SERVICE_ACCOUNT=/Users/udhaya10/workspace/BlueDot-Trading-System/.credentials/google-drive-service-account.json

# Google Drive Folder IDs
DAILY_FOLDER_ID=1-L9PF0zZqtalEHdVPkHLeGDAyuvN5MUo
WEEKLY_FOLDER_ID=1-LY72Ml_FXr5SJK8wCySlSMB78OU6gM4

# GitHub Configuration
GITHUB_USERNAME=udhaya10
GITHUB_PAGES_URL=https://udhaya10.github.io/BlueDot-Trading-System

# TradingView Configuration
TRADINGVIEW_NAMESPACE=stocks_chimmu_ms

# Processing Configuration
PROCESSING_MODE=development
DEBUG_MODE=true
LOG_LEVEL=INFO
MAX_FILES_PER_BATCH=100
PARALLEL_WORKERS=4
MEMORY_LIMIT_GB=8
```

## 📦 Python Environment

### Virtual Environment
- **Location**: `/Users/udhaya10/workspace/BlueDot-Trading-System/venv`
- **Python Version**: 3.12.6
- **Activation**: `source venv/bin/activate`

### Key Dependencies Installed
- Google API Python Client
- Google Auth libraries
- Pandas, NumPy for data processing
- PyYAML for configuration
- Python-dotenv for environment variables

## 📅 Automation Schedule

### GitHub Actions Pipeline Schedule
- **Daily Pipeline**: Runs at **9:00 AM UTC** every day
  - 4:00 AM EST / 1:00 AM PST / 2:30 PM IST
  - Processes files from Daily Google Drive folder
  
- **Weekly Pipeline**: Runs at **10:00 AM UTC** every Sunday
  - 5:00 AM EST / 2:00 AM PST / 3:30 PM IST
  - Processes files from Weekly Google Drive folder

### Manual Triggers
All workflows support manual execution via GitHub Actions tab with optional date/week parameters.

## 🚀 Quick Start Commands

### Activate Environment
```bash
source venv/bin/activate
```

### Test Google Drive Connection
```bash
python test_google_drive.py
```

### Process Daily Batch
```bash
python src/batch_processing/batch_processor.py --timeframe daily --date 2024-08-02
```

### Process Weekly Batch
```bash
python src/batch_processing/batch_processor.py --timeframe weekly --date 2024-W31
```

## ✅ Setup Verification Checklist

- [x] Service account JSON file in place
- [x] `.credentials` directory created with proper permissions
- [x] `.env` file configured with all IDs and settings
- [x] `.gitignore` file created to protect credentials
- [x] Python virtual environment created
- [x] All dependencies installed
- [x] Google Drive folders shared with service account
- [x] Google Drive connection tested and working
- [ ] Sample data processing tested
- [ ] GitHub Actions configured
- [ ] First deployment to GitHub Pages

## 🔑 Important Files

1. **Credentials**: `.credentials/google-drive-service-account.json`
2. **Environment Config**: `.env`
3. **Git Ignore**: `.gitignore`
4. **Test Script**: `test_google_drive.py`
5. **Main Processor**: `src/batch_processing/batch_processor.py`

## 📝 Notes

- The service account has read-only access to prevent accidental modifications
- All sensitive files are excluded from git tracking
- The system is configured for development mode with debug logging enabled
- Ready for production deployment with GitHub Actions

---

**Remember**: Never commit credentials or the `.env` file to version control!