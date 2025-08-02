#!/usr/bin/env python3
"""
Alerting system for BlueDot Trading System
Supports Slack and Discord webhooks for production monitoring
"""

import json
import requests
import logging
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertManager:
    """Manages alerts across multiple channels"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.slack_webhook = config.get('slack_webhook_url')
        self.discord_webhook = config.get('discord_webhook_url')
        
    def send_alert(self, 
                   title: str, 
                   message: str, 
                   level: AlertLevel = AlertLevel.INFO,
                   details: Optional[Dict] = None,
                   metrics: Optional[Dict] = None):
        """Send alert to all configured channels"""
        
        # Send to Slack
        if self.slack_webhook:
            self._send_slack_alert(title, message, level, details, metrics)
        
        # Send to Discord
        if self.discord_webhook:
            self._send_discord_alert(title, message, level, details, metrics)
        
        # Log locally
        self.logger.log(
            getattr(logging, level.value.upper()),
            f"{title}: {message}",
            extra={'details': details, 'metrics': metrics}
        )
    
    def _send_slack_alert(self, title: str, message: str, level: AlertLevel, 
                          details: Optional[Dict], metrics: Optional[Dict]):
        """Send alert to Slack"""
        color_map = {
            AlertLevel.INFO: "#36a64f",
            AlertLevel.WARNING: "#ff9900",
            AlertLevel.ERROR: "#ff0000",
            AlertLevel.CRITICAL: "#990000"
        }
        
        payload = {
            "attachments": [{
                "color": color_map[level],
                "title": f"{level.value.upper()}: {title}",
                "text": message,
                "fields": [],
                "footer": "BlueDot Trading System",
                "ts": int(datetime.now().timestamp())
            }]
        }
        
        # Add details fields
        if details:
            for key, value in details.items():
                payload["attachments"][0]["fields"].append({
                    "title": key,
                    "value": str(value),
                    "short": True
                })
        
        # Add metrics fields
        if metrics:
            for key, value in metrics.items():
                payload["attachments"][0]["fields"].append({
                    "title": f"📊 {key}",
                    "value": str(value),
                    "short": True
                })
        
        try:
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            response.raise_for_status()
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {e}")
    
    def _send_discord_alert(self, title: str, message: str, level: AlertLevel,
                            details: Optional[Dict], metrics: Optional[Dict]):
        """Send alert to Discord"""
        color_map = {
            AlertLevel.INFO: 0x00ff00,
            AlertLevel.WARNING: 0xffa500,
            AlertLevel.ERROR: 0xff0000,
            AlertLevel.CRITICAL: 0x8b0000
        }
        
        embed = {
            "title": f"{level.value.upper()}: {title}",
            "description": message,
            "color": color_map[level],
            "fields": [],
            "footer": {"text": "BlueDot Trading System"},
            "timestamp": datetime.now().isoformat()
        }
        
        # Add fields
        if details:
            for key, value in details.items():
                embed["fields"].append({
                    "name": key,
                    "value": str(value),
                    "inline": True
                })
        
        if metrics:
            for key, value in metrics.items():
                embed["fields"].append({
                    "name": f"📊 {key}",
                    "value": str(value),
                    "inline": True
                })
        
        payload = {"embeds": [embed]}
        
        try:
            response = requests.post(self.discord_webhook, json=payload, timeout=10)
            response.raise_for_status()
        except Exception as e:
            self.logger.error(f"Failed to send Discord alert: {e}")

class ProcessingMonitor:
    """Monitor data processing pipelines"""
    
    def __init__(self, alert_manager: AlertManager):
        self.alert_manager = alert_manager
        self.start_time = None
        self.metrics = {
            'files_processed': 0,
            'files_failed': 0,
            'validation_errors': 0,
            'processing_time': 0
        }
    
    def start_processing(self, total_files: int, timeframe: str, date: str):
        """Mark start of processing"""
        self.start_time = datetime.now()
        self.metrics = {
            'files_processed': 0,
            'files_failed': 0,
            'validation_errors': 0,
            'processing_time': 0
        }
        
        self.alert_manager.send_alert(
            title="Processing Started",
            message=f"Starting {timeframe} processing for {date}",
            level=AlertLevel.INFO,
            details={
                'timeframe': timeframe,
                'date': date,
                'total_files': total_files
            }
        )
    
    def file_processed(self, symbol: str, success: bool, error: Optional[str] = None):
        """Track individual file processing"""
        if success:
            self.metrics['files_processed'] += 1
        else:
            self.metrics['files_failed'] += 1
            
            # Send alert for critical failures
            if self.metrics['files_failed'] > 10:
                self.alert_manager.send_alert(
                    title="High Failure Rate",
                    message=f"More than 10 files have failed processing",
                    level=AlertLevel.ERROR,
                    details={'symbol': symbol, 'error': error},
                    metrics=self.metrics
                )
    
    def validation_error(self, symbol: str, validation_errors: List[str]):
        """Track validation errors"""
        self.metrics['validation_errors'] += len(validation_errors)
        
        # Alert on validation issues
        self.alert_manager.send_alert(
            title="Data Validation Failed",
            message=f"Validation errors found for {symbol}",
            level=AlertLevel.WARNING,
            details={
                'symbol': symbol,
                'errors': ', '.join(validation_errors[:3])  # First 3 errors
            }
        )
    
    def end_processing(self, status: str = "completed"):
        """Mark end of processing"""
        if self.start_time:
            self.metrics['processing_time'] = (datetime.now() - self.start_time).total_seconds()
        
        # Determine alert level based on metrics
        if self.metrics['files_failed'] > 0:
            level = AlertLevel.ERROR if self.metrics['files_failed'] > 5 else AlertLevel.WARNING
        else:
            level = AlertLevel.INFO
        
        # Calculate success rate
        total = self.metrics['files_processed'] + self.metrics['files_failed']
        success_rate = (self.metrics['files_processed'] / total * 100) if total > 0 else 0
        
        self.alert_manager.send_alert(
            title="Processing Completed",
            message=f"Processing {status} with {success_rate:.1f}% success rate",
            level=level,
            metrics={
                'Files Processed': self.metrics['files_processed'],
                'Files Failed': self.metrics['files_failed'],
                'Validation Errors': self.metrics['validation_errors'],
                'Processing Time': f"{self.metrics['processing_time']:.1f}s",
                'Success Rate': f"{success_rate:.1f}%"
            }
        )
    
    def critical_error(self, error: str, context: Optional[Dict] = None):
        """Report critical errors"""
        self.alert_manager.send_alert(
            title="Critical Error",
            message=error,
            level=AlertLevel.CRITICAL,
            details=context
        )