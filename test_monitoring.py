#!/usr/bin/env python3
"""
Test monitoring and alerting system
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from src.monitoring.alerting import AlertManager, ProcessingMonitor, AlertLevel
from src.monitoring.health_check import HealthChecker, HealthCheckAPI
import json

def test_alerting():
    """Test alerting functionality"""
    print("🧪 Testing Alerting System")
    print("=" * 50)
    
    # Load config
    config = {
        'slack_webhook_url': os.getenv('SLACK_WEBHOOK_URL'),
        'discord_webhook_url': os.getenv('DISCORD_WEBHOOK_URL')
    }
    
    if not config['slack_webhook_url'] and not config['discord_webhook_url']:
        print("⚠️  No webhooks configured. Run setup_monitoring.py first.")
        return
    
    alert_manager = AlertManager(config)
    
    # Test different alert levels
    print("\n📤 Sending test alerts...")
    
    # Info alert
    alert_manager.send_alert(
        title="System Started",
        message="BlueDot Trading System monitoring is active",
        level=AlertLevel.INFO,
        details={'version': '1.0.0', 'environment': 'production'}
    )
    
    # Warning alert
    alert_manager.send_alert(
        title="High Memory Usage",
        message="Memory usage exceeded 75% threshold",
        level=AlertLevel.WARNING,
        details={'current_usage': '78%', 'threshold': '75%'},
        metrics={'memory_mb': 6234, 'available_mb': 1766}
    )
    
    # Error alert
    alert_manager.send_alert(
        title="Processing Failed",
        message="Failed to process 5 files due to validation errors",
        level=AlertLevel.ERROR,
        details={'failed_files': 'AAPL, GOOGL, MSFT, AMZN, TSLA'},
        metrics={'success_rate': '92%', 'failed_count': 5}
    )
    
    print("✅ Test alerts sent!")

def test_processing_monitor():
    """Test processing monitor"""
    print("\n🧪 Testing Processing Monitor")
    print("=" * 50)
    
    config = {
        'slack_webhook_url': os.getenv('SLACK_WEBHOOK_URL'),
        'discord_webhook_url': os.getenv('DISCORD_WEBHOOK_URL')
    }
    
    alert_manager = AlertManager(config)
    monitor = ProcessingMonitor(alert_manager)
    
    # Simulate processing
    print("\n📊 Simulating batch processing...")
    
    # Start processing
    monitor.start_processing(total_files=100, timeframe='daily', date='2024-08-02')
    
    # Simulate file processing
    for i in range(95):
        monitor.file_processed(f'STOCK{i}', success=True)
    
    # Simulate some failures
    for i in range(5):
        monitor.file_processed(f'FAIL{i}', success=False, error='Invalid JSON structure')
    
    # End processing
    monitor.end_processing()
    
    print("✅ Processing simulation completed!")

def test_health_check():
    """Test health check system"""
    print("\n🧪 Testing Health Check System")
    print("=" * 50)
    
    # Load config
    with open('config/data_config.yaml', 'r') as f:
        import yaml
        config = yaml.safe_load(f)
    
    health_checker = HealthChecker(config)
    api = HealthCheckAPI(health_checker)
    
    # Get health status
    print("\n🏥 System Health Status:")
    health = api.get_health_status()
    
    print(f"Status: {health['status']}")
    print(f"Issues: {len(health['issues'])}")
    
    if health['issues']:
        print("\n⚠️  Issues detected:")
        for issue in health['issues']:
            print(f"  - [{issue['severity']}] {issue['type']}: {issue['message']}")
    
    # Print metrics
    print("\n📊 System Metrics:")
    metrics = health['metrics']['system']
    print(f"  CPU: {metrics['cpu_percent']}%")
    print(f"  Memory: {metrics['memory_percent']}%")
    print(f"  Disk: {metrics['disk_usage_percent']}%")
    
    # Simple status
    simple = api.get_simple_status()
    print(f"\n✅ Simple Status: {'Healthy' if simple['healthy'] else 'Unhealthy'}")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    test_alerting()
    test_processing_monitor()
    test_health_check()
    
    print("\n✅ All monitoring tests completed!")