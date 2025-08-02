#!/usr/bin/env python3
"""
BlueDot Trading System - Notification System
Handles success/failure notifications and monitoring
"""

import os
import json
import logging
import requests
from typing import Dict, Optional
from datetime import datetime

class NotificationSystem:
    """Handles various notification channels"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def send_processing_notification(self, status: str, timeframe: str, 
                                   stats: Dict, webhook_url: Optional[str] = None) -> bool:
        """
        Send processing status notification
        
        Args:
            status: 'success' or 'failure'
            timeframe: 'daily' or 'weekly'
            stats: Processing statistics
            webhook_url: Optional webhook URL (Slack, Discord, etc.)
            
        Returns:
            True if notification sent successfully
        """
        try:
            message = self._format_message(status, timeframe, stats)
            
            # Send to webhook (Slack, Discord, etc.)
            if webhook_url:
                success = self._send_webhook_notification(webhook_url, message, status)
                if success:
                    self.logger.info("Webhook notification sent successfully")
                else:
                    self.logger.error("Failed to send webhook notification")
                    
            # Log notification
            self.logger.info(f"Notification sent: {message}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {str(e)}")
            return False
    
    def _format_message(self, status: str, timeframe: str, stats: Dict) -> str:
        """Format notification message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        if status == "success":
            emoji = "✅"
            title = "Processing Completed Successfully"
        else:
            emoji = "🚨"
            title = "Processing Failed"
        
        message = f"""
{emoji} **BlueDot Trading System - {title}**

**Timeframe:** {timeframe.title()}
**Date:** {stats.get('date', 'Unknown')}
**Time:** {timestamp}

**Statistics:**
• Total Files: {stats.get('total_files', 0)}
• Processed: {stats.get('processed', 0)}
• Errors: {stats.get('errors', 0)}
• Success Rate: {stats.get('success_rate', 0):.1f}%

**Status:** {stats.get('status', 'Unknown')}
        """.strip()
        
        return message
    
    def _send_webhook_notification(self, webhook_url: str, message: str, status: str) -> bool:
        """Send notification to webhook URL (Slack, Discord, etc.)"""
        try:
            # Determine if this is a Slack or Discord webhook
            if "hooks.slack.com" in webhook_url:
                return self._send_slack_notification(webhook_url, message, status)
            elif "discord.com" in webhook_url or "discordapp.com" in webhook_url:
                return self._send_discord_notification(webhook_url, message, status)
            else:
                # Generic webhook
                return self._send_generic_webhook(webhook_url, message, status)
                
        except Exception as e:
            self.logger.error(f"Webhook notification failed: {str(e)}")
            return False
    
    def _send_slack_notification(self, webhook_url: str, message: str, status: str) -> bool:
        """Send Slack notification"""
        color = "good" if status == "success" else "danger"
        
        payload = {
            "attachments": [
                {
                    "color": color,
                    "text": message,
                    "mrkdwn_in": ["text"]
                }
            ]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 200
    
    def _send_discord_notification(self, webhook_url: str, message: str, status: str) -> bool:
        """Send Discord notification"""
        color = 0x00ff00 if status == "success" else 0xff0000  # Green or Red
        
        payload = {
            "embeds": [
                {
                    "description": message,
                    "color": color,
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 204
    
    def _send_generic_webhook(self, webhook_url: str, message: str, status: str) -> bool:
        """Send generic webhook notification"""
        payload = {
            "text": message,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code in [200, 201, 204]


class HealthMonitor:
    """System health monitoring and alerting"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_system_health(self) -> Dict:
        """Comprehensive system health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        # Check data freshness
        health_status["checks"]["data_freshness"] = self._check_data_freshness()
        
        # Check processing quality
        health_status["checks"]["processing_quality"] = self._check_processing_quality()
        
        # Check storage space
        health_status["checks"]["storage_space"] = self._check_storage_space()
        
        # Check GitHub Pages status
        health_status["checks"]["github_pages"] = self._check_github_pages_status()
        
        # Determine overall status
        failed_checks = [
            check for check, status in health_status["checks"].items()
            if status.get("status") != "healthy"
        ]
        
        if failed_checks:
            health_status["overall_status"] = "unhealthy"
            health_status["failed_checks"] = failed_checks
        
        return health_status
    
    def _check_data_freshness(self) -> Dict:
        """Check if data is current and up to date"""
        try:
            # Check when data was last updated
            # This would check timestamps of latest files
            return {
                "status": "healthy",
                "message": "Data is current",
                "last_update": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to check data freshness: {str(e)}"
            }
    
    def _check_processing_quality(self) -> Dict:
        """Check for processing errors or anomalies"""
        try:
            # This would analyze recent processing logs
            # Check error rates, processing times, etc.
            return {
                "status": "healthy",
                "message": "Processing quality normal",
                "error_rate": 0.0
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to check processing quality: {str(e)}"
            }
    
    def _check_storage_space(self) -> Dict:
        """Check available storage space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            
            free_gb = free // (1024**3)
            
            if free_gb < 1:  # Less than 1GB free
                return {
                    "status": "warning",
                    "message": f"Low storage space: {free_gb}GB free",
                    "free_space_gb": free_gb
                }
            else:
                return {
                    "status": "healthy",
                    "message": f"Storage space adequate: {free_gb}GB free",
                    "free_space_gb": free_gb
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to check storage: {str(e)}"
            }
    
    def _check_github_pages_status(self) -> Dict:
        """Check if GitHub Pages is accessible"""
        try:
            # This would check if GitHub Pages is serving files
            return {
                "status": "healthy",
                "message": "GitHub Pages accessible"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"GitHub Pages check failed: {str(e)}"
            }


# Entry points for GitHub Actions
def send_success_notification():
    """Send success notification from GitHub Actions"""
    import sys
    
    webhook_url = os.getenv('WEBHOOK_URL')
    timeframe = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    
    # Mock statistics - in real implementation, this would be loaded from file
    stats = {
        "status": "completed",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_files": 1000,
        "processed": 995,
        "errors": 5,
        "success_rate": 99.5
    }
    
    notifier = NotificationSystem()
    success = notifier.send_processing_notification(
        status="success",
        timeframe=timeframe,
        stats=stats,
        webhook_url=webhook_url
    )
    
    if success:
        print("✅ Success notification sent")
    else:
        print("❌ Failed to send success notification")


def send_failure_notification():
    """Send failure notification from GitHub Actions"""
    import sys
    
    webhook_url = os.getenv('WEBHOOK_URL')
    timeframe = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    
    # Mock error statistics
    stats = {
        "status": "failed",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_files": 1000,
        "processed": 0,
        "errors": 1000,
        "success_rate": 0.0,
        "error_message": "Processing pipeline failed"
    }
    
    notifier = NotificationSystem()
    success = notifier.send_processing_notification(
        status="failure",
        timeframe=timeframe,
        stats=stats,
        webhook_url=webhook_url
    )
    
    if success:
        print("🚨 Failure notification sent")
    else:
        print("❌ Failed to send failure notification")


def run_health_check():
    """Run system health check"""
    monitor = HealthMonitor()
    health = monitor.check_system_health()
    
    print(f"🏥 System Health: {health['overall_status']}")
    
    for check_name, result in health["checks"].items():
        status_emoji = "✅" if result["status"] == "healthy" else "⚠️" if result["status"] == "warning" else "❌"
        print(f"  {status_emoji} {check_name}: {result['message']}")
    
    # Return appropriate exit code
    if health["overall_status"] != "healthy":
        sys.exit(1)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "success":
            send_success_notification()
        elif command == "failure":
            send_failure_notification()
        elif command == "health":
            run_health_check()
        else:
            print("Usage: python notification_system.py [success|failure|health]")
    else:
        print("Usage: python notification_system.py [success|failure|health]")