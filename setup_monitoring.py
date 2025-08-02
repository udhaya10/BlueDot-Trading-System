#!/usr/bin/env python3
"""
Setup script for monitoring and alerting configuration
"""

import os
import json
from pathlib import Path

def setup_monitoring():
    """Interactive setup for monitoring configuration"""
    print("🔔 BlueDot Trading System - Monitoring Setup")
    print("=" * 50)
    
    # Check if .env exists
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found. Please run setup.sh first.")
        return
    
    print("\nThis will help you configure monitoring and alerting.")
    print("You can set up Slack and/or Discord webhooks for notifications.")
    
    # Slack setup
    print("\n📣 Slack Configuration")
    print("To get a Slack webhook URL:")
    print("1. Go to https://api.slack.com/apps")
    print("2. Create a new app or select existing")
    print("3. Add 'Incoming Webhooks' feature")
    print("4. Create a webhook for your channel")
    
    slack_webhook = input("\nEnter Slack webhook URL (or press Enter to skip): ").strip()
    
    # Discord setup
    print("\n🎮 Discord Configuration")
    print("To get a Discord webhook URL:")
    print("1. Go to your Discord channel settings")
    print("2. Select 'Integrations' → 'Webhooks'")
    print("3. Create a new webhook")
    print("4. Copy the webhook URL")
    
    discord_webhook = input("\nEnter Discord webhook URL (or press Enter to skip): ").strip()
    
    # Update .env file
    if slack_webhook or discord_webhook:
        print("\n✍️  Updating configuration...")
        
        # Read existing .env
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Update or add webhook URLs
        updated = False
        new_lines = []
        
        for line in lines:
            if line.startswith('SLACK_WEBHOOK_URL='):
                if slack_webhook:
                    new_lines.append(f'SLACK_WEBHOOK_URL={slack_webhook}\n')
                    updated = True
                else:
                    new_lines.append(line)
            elif line.startswith('DISCORD_WEBHOOK_URL='):
                if discord_webhook:
                    new_lines.append(f'DISCORD_WEBHOOK_URL={discord_webhook}\n')
                    updated = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        # Add new entries if not found
        if slack_webhook and not any('SLACK_WEBHOOK_URL=' in line for line in lines):
            new_lines.append(f'\n# Monitoring Webhooks\n')
            new_lines.append(f'SLACK_WEBHOOK_URL={slack_webhook}\n')
        
        if discord_webhook and not any('DISCORD_WEBHOOK_URL=' in line for line in lines):
            if not slack_webhook:
                new_lines.append(f'\n# Monitoring Webhooks\n')
            new_lines.append(f'DISCORD_WEBHOOK_URL={discord_webhook}\n')
        
        # Write updated .env
        with open('.env', 'w') as f:
            f.writelines(new_lines)
        
        print("✅ Monitoring configuration updated!")
        
        # Test webhooks
        print("\n🧪 Testing webhooks...")
        test_monitoring(slack_webhook, discord_webhook)
    else:
        print("\n⚠️  No webhooks configured. You can add them later to .env file.")

def test_monitoring(slack_webhook: str, discord_webhook: str):
    """Test webhook configurations"""
    import sys
    sys.path.append(os.path.dirname(__file__))
    
    from src.monitoring.alerting import AlertManager, AlertLevel
    
    config = {
        'slack_webhook_url': slack_webhook,
        'discord_webhook_url': discord_webhook
    }
    
    alert_manager = AlertManager(config)
    
    # Send test alert
    alert_manager.send_alert(
        title="Test Alert",
        message="This is a test alert from BlueDot Trading System setup",
        level=AlertLevel.INFO,
        details={
            'setup_status': 'complete',
            'test': 'successful'
        },
        metrics={
            'test_metric': 123,
            'success_rate': '100%'
        }
    )
    
    print("\n✅ Test alerts sent! Check your Slack/Discord channels.")

if __name__ == "__main__":
    setup_monitoring()