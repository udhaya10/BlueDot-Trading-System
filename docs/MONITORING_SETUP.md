# Monitoring and Alerting Setup

This guide explains how to set up monitoring and alerting for the BlueDot Trading System.

## Overview

The monitoring system provides:
- **Real-time alerts** via Slack and Discord
- **Processing status updates** (start, progress, completion)
- **Error notifications** with detailed context
- **Health checks** for system resources
- **Data validation alerts**

## Alert Levels

- 🟢 **INFO**: Normal operational messages
- 🟡 **WARNING**: Issues that need attention but aren't critical
- 🔴 **ERROR**: Processing failures or serious issues
- 🟣 **CRITICAL**: System-level failures requiring immediate attention

## Setup Instructions

### 1. Slack Integration

1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app or select existing one
3. Add "Incoming Webhooks" feature
4. Create a webhook for your desired channel
5. Copy the webhook URL

### 2. Discord Integration

1. Go to your Discord channel settings
2. Select "Integrations" → "Webhooks"
3. Create a new webhook
4. Copy the webhook URL

### 3. Configure Webhooks

Run the setup script:
```bash
python setup_monitoring.py
```

Or manually add to `.env`:
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK/URL
```

### 4. GitHub Actions Secrets

Add these secrets to your GitHub repository:
1. Go to Settings → Secrets and variables → Actions
2. Add:
   - `SLACK_WEBHOOK_URL` (optional)
   - `DISCORD_WEBHOOK_URL` (optional)

## Testing

Test your monitoring setup:
```bash
python test_monitoring.py
```

This will:
- Send test alerts to all configured channels
- Simulate a processing run
- Check system health

## Alert Examples

### Processing Started
```
INFO: Processing Started
Starting daily processing for 2024-08-02
- timeframe: daily
- date: 2024-08-02
- total_files: 1000
```

### Processing Completed
```
INFO: Processing Completed
Processing completed with 98.5% success rate
📊 Files Processed: 985
📊 Files Failed: 15
📊 Processing Time: 2745.3s
📊 Success Rate: 98.5%
```

### Validation Error
```
WARNING: Data Validation Failed
Validation errors found for AAPL
- symbol: AAPL
- errors: Missing fields: rlst, bc
```

### Critical Error
```
CRITICAL: Critical Error
Batch processing failed: Connection timeout
- timeframe: daily
- date: 2024-08-02
```

## Health Checks

The system monitors:
- CPU usage (alert if >90%)
- Memory usage (alert if >85%)
- Disk usage (alert if >80%)
- Pipeline staleness (alert if >26 hours)
- Data quality metrics

## Custom Alerts

Add custom alerts in your code:
```python
from src.monitoring.alerting import AlertManager, AlertLevel

alert_manager = AlertManager(config)
alert_manager.send_alert(
    title="Custom Alert",
    message="Your custom message here",
    level=AlertLevel.INFO,
    details={'key': 'value'},
    metrics={'metric': 123}
)
```

## Troubleshooting

### No alerts received
1. Check webhook URLs are correct
2. Verify GitHub Secrets are set
3. Check logs in `logs/monitoring_events.log`

### Test webhooks manually
```bash
# Slack
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message"}' \
  YOUR_SLACK_WEBHOOK_URL

# Discord  
curl -X POST -H 'Content-type: application/json' \
  --data '{"content":"Test message"}' \
  YOUR_DISCORD_WEBHOOK_URL
```