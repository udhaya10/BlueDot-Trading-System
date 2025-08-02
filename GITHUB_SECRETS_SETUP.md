# GitHub Secrets Setup Guide

This guide will help you configure the necessary GitHub secrets for automated daily and weekly processing.

## Required Secrets

You need to add the following secrets to your GitHub repository:

### 1. `GOOGLE_DRIVE_SERVICE_ACCOUNT` (Required)
The base64-encoded content of your service account JSON file.

**How to encode:**
```bash
# On macOS/Linux:
base64 -i .credentials/google-drive-service-account.json | pbcopy

# On Linux (without pbcopy):
base64 .credentials/google-drive-service-account.json

# On Windows (PowerShell):
[Convert]::ToBase64String([IO.File]::ReadAllBytes(".credentials\google-drive-service-account.json"))
```

### 2. `DAILY_FOLDER_ID` (Required)
Your Google Drive daily folder ID.
- Value: `1-L9PF0zZqtalEHdVPkHLeGDAyuvN5MUo`

### 3. `WEEKLY_FOLDER_ID` (Required)
Your Google Drive weekly folder ID.
- Value: `1-LY72Ml_FXr5SJK8wCySlSMB78OU6gM4`

### 4. `TRADINGVIEW_NAMESPACE` (Required)
Your TradingView namespace for data access.
- Value: `stocks_chimmu_ms`

## How to Add Secrets to GitHub

1. Go to your repository on GitHub
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with the name and value specified above

## Step-by-Step for Service Account Secret

1. **Encode your service account file:**
   ```bash
   base64 -i .credentials/google-drive-service-account.json > service-account-base64.txt
   ```

2. **Copy the encoded content:**
   - Open `service-account-base64.txt`
   - Copy the entire content (it will be one long string)

3. **Add to GitHub:**
   - Secret name: `GOOGLE_DRIVE_SERVICE_ACCOUNT`
   - Secret value: Paste the base64-encoded content
   - Click "Add secret"

4. **Clean up:**
   ```bash
   rm service-account-base64.txt
   ```

## Verification Checklist

After adding all secrets, verify you have:

- [ ] `GOOGLE_DRIVE_SERVICE_ACCOUNT` - Base64-encoded service account JSON
- [ ] `DAILY_FOLDER_ID` - Set to `1-L9PF0zZqtalEHdVPkHLeGDAyuvN5MUo`
- [ ] `WEEKLY_FOLDER_ID` - Set to `1-LY72Ml_FXr5SJK8wCySlSMB78OU6gM4`
- [ ] `TRADINGVIEW_NAMESPACE` - Set to `stocks_chimmu_ms`

## Automation Schedule

Once configured, the workflows will run automatically:
- **Daily Pipeline**: 9:00 AM UTC (4 AM EST / 1 AM PST / 2:30 PM IST)
- **Weekly Pipeline**: 10:00 AM UTC Sundays (5 AM EST / 2 AM PST / 3:30 PM IST)

## Testing the Workflows

### Manual Trigger Test

1. Go to the **Actions** tab in your repository
2. Select either "Daily Processing Pipeline" or "Weekly Processing Pipeline"
3. Click **Run workflow**
4. Optionally specify a date/week
5. Click **Run workflow** button

### Monitoring

- Check the **Actions** tab for workflow runs
- Each run will show:
  - Download progress
  - Processing status
  - Number of files processed
  - Deployment status

## GitHub Pages Setup

1. Go to **Settings** → **Pages**
2. Source: Deploy from a branch
3. Branch: `gh-pages` (will be created automatically)
4. Folder: `/ (root)`
5. Click Save

After the first successful run, your data will be available at:
```
https://udhaya10.github.io/BlueDot-Trading-System/data/daily/
https://udhaya10.github.io/BlueDot-Trading-System/data/weekly/
```

## Troubleshooting

### "Bad credentials" error
- Ensure the service account JSON is properly base64-encoded
- Check that you copied the entire encoded string

### "File not found" errors
- Verify the folder IDs are correct
- Ensure the service account has access to both folders

### No output files
- Check that JSON files exist in your Google Drive folders
- Verify the files follow the expected format

## Security Notes

- Never commit secrets to your repository
- GitHub secrets are encrypted and only exposed to workflows
- The service account has read-only access to minimize risk
- Regularly rotate credentials if needed