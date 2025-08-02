# Troubleshooting Guide

This guide helps resolve common issues with the BlueDot Trading System.

## Common Issues and Solutions

### 1. Blue Dots Showing All Zeros

**Problem**: The BLUE_DOTS.csv file shows 0 for all rows even though blue dot dates exist in the JSON.

**Cause**: The blueDotData is located at `json_data['chart']['blueDotData']['dates']` not at the top level.

**Solution**: Already fixed in the codebase. The batch processor now correctly accesses:
```python
blue_dot_signals = self._generate_blue_dot_signals(
    json_data.get('chart', {}).get('blueDotData', {}), 
    prices
)
```

**Verification**: Check that blue dots match dates in the JSON:
- Blue dot dates are in "YYYY-MM-DD" format (e.g., "2024-11-08")
- The processor converts price timestamps to date strings for comparison

### 2. Weekly Processing Not Working

**Problem**: Weekly processing workflow fails or doesn't trigger properly.

**Solution**: The workflow has been updated to use the unified `process_from_drive.py` script:
```bash
python process_from_drive.py --timeframe weekly --date 2024-W46
```

**Key points**:
- Weekly workflows run every Sunday at 10 AM UTC
- Week format must be YYYY-WXX (e.g., 2024-W46)
- Manual trigger available in GitHub Actions

### 3. GitHub Pages Daily Folder Deleted When Weekly Runs

**Problem**: Running weekly workflow deletes the daily folder from GitHub Pages.

**Solution**: Both workflows now use `keep_files: true` in the deployment step:
```yaml
- name: 🚀 Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    keep_files: true  # Preserves existing files
```

### 4. Google Drive Permission Denied (404 Error)

**Problem**: Getting "404 File not found" error when accessing Google Drive folders.

**Solution**: 
1. Get the service account email from your JSON key file
2. Share both Google Drive folders with this email address
3. Grant "Viewer" permissions
4. Test again with `python scripts/test_google_drive_connection.py`

### 5. TradingView Can't Access Data

**Problem**: request.seed() returns no data in Pine Script.

**Solutions**:
1. **Check GitHub Pages deployment**:
   - Visit: https://YOUR_USERNAME.github.io/BlueDot-Trading-System/data/daily/
   - Verify CSV files are accessible

2. **Verify namespace format**:
   ```pine
   // Correct format:
   request.seed('stocks_chimmu_ms_daily_AAPL', 'BLUE_DOTS', close)
   
   // NOT:
   request.seed('stocks_chimmu_ms_daily_AAPL_BLUE_DOTS', 'DOTS', close)
   ```

3. **Check column names**:
   - Use 'BLUE_DOTS' not 'DOTS'
   - Use 'RLST_RATING' not 'RLST'
   - Use 'BC_INDICATOR' not 'BC'

### 6. Processing Takes Too Long

**Problem**: GitHub Actions timeout after 2-3 hours with large datasets.

**Solutions**:
1. **Increase parallel workers** in `.env`:
   ```bash
   PARALLEL_WORKERS=8  # Default is 4
   ```

2. **Process in batches**:
   - Split files across multiple folders
   - Run separate workflows for different stock groups

3. **Optimize file sizes**:
   - Ensure JSON files only contain necessary data
   - Remove duplicate or historical data beyond needed range

### 7. Git Commits Include Venv Files

**Problem**: When committing, git adds hundreds of venv files.

**Solution**: 
1. Reset the staging area:
   ```bash
   git reset
   ```

2. Add only relevant files:
   ```bash
   git add .github/ src/ docs/ *.md *.py
   git commit -m "Your message"
   ```

3. Ensure `.gitignore` includes:
   ```
   venv/
   __pycache__/
   *.pyc
   .env
   ```

### 8. Service Account JSON Encoding

**Problem**: "Invalid base64" error in GitHub Actions.

**Solution**: Properly encode your service account JSON:
```bash
# macOS:
base64 -i google-drive-service-account.json | pbcopy

# Linux:
base64 google-drive-service-account.json | xclip

# Windows:
certutil -encode google-drive-service-account.json encoded.txt
```

Then paste the encoded string into GitHub Secrets.

### 9. Date Format Issues

**Problem**: Daily/weekly date formats not recognized.

**Solution**: Use correct formats:
- Daily: `YYYY-MM-DD` (e.g., 2024-11-12)
- Weekly: `YYYY-WXX` (e.g., 2024-W46)

The system automatically handles these in the workflows:
```bash
# Daily
python process_from_drive.py --timeframe daily --date 2024-11-12

# Weekly  
python process_from_drive.py --timeframe weekly --date 2024-W46
```

### 10. Missing Dependencies

**Problem**: Import errors when running locally.

**Solution**: Install all requirements:
```bash
pip install -r requirements.txt
pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib python-dotenv
```

## Debug Commands

### Check Current Configuration
```bash
# View environment variables
cat .env

# Test Google Drive connection
python scripts/test_google_drive_connection.py

# Process single file locally
python src/batch_processing/batch_processor.py --timeframe daily --date 2024-11-12
```

### Verify Output Structure
```bash
# Check output directory
ls -la data/output/daily/2024-11-12/

# Verify CSV format
head -5 data/output/daily/2024-11-12/AAPL_BLUE_DOTS.csv
```

### GitHub Actions Debugging
1. Go to Actions tab in your repository
2. Click on a failed workflow run
3. Expand the failed step to see detailed logs
4. Look for error messages and stack traces

## Getting Help

If you encounter issues not covered here:

1. **Check the logs**: GitHub Actions provides detailed logs for each run
2. **Review the code**: Most processing logic is in `src/batch_processing/batch_processor.py`
3. **Test locally**: Run the scripts locally with sample data to debug
4. **Check permissions**: Ensure all API keys and folder permissions are correct

## Recent Fixes Applied

1. **Blue Dot Processing**: Fixed to look inside `chart.blueDotData.dates`
2. **Weekly Workflow**: Updated to use unified `process_from_drive.py` script
3. **File Preservation**: Both workflows now keep existing files when deploying
4. **Date Comparison**: Fixed to handle string date format in blue dot matching