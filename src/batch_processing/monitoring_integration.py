#!/usr/bin/env python3
"""
Integration of monitoring into batch processing pipeline
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from ..monitoring.alerting import AlertManager, ProcessingMonitor, AlertLevel
from ..monitoring.health_check import HealthChecker
from .batch_processor import BatchProcessor

class MonitoredBatchProcessor(BatchProcessor):
    """Batch processor with integrated monitoring and alerting"""
    
    def __init__(self, config_path: str = "config/data_config.yaml"):
        super().__init__(config_path)
        
        # Initialize monitoring
        monitoring_config = {
            'slack_webhook_url': os.getenv('SLACK_WEBHOOK_URL'),
            'discord_webhook_url': os.getenv('DISCORD_WEBHOOK_URL')
        }
        
        self.alert_manager = AlertManager(monitoring_config)
        self.monitor = ProcessingMonitor(self.alert_manager)
        self.health_checker = HealthChecker(self.config)
        
        # Setup monitoring logger
        self._setup_monitoring_logger()
    
    def _setup_monitoring_logger(self):
        """Setup separate logger for monitoring events"""
        monitor_logger = logging.getLogger('monitoring')
        
        # Create logs directory
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Add file handler for monitoring events
        handler = logging.FileHandler('logs/monitoring_events.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        monitor_logger.addHandler(handler)
    
    def process_timeframe_batch(self, timeframe: str, date: str) -> Dict:
        """Process batch with monitoring"""
        try:
            # Check system health before starting
            health_status = self.health_checker.get_health_status()
            if health_status['status'] == 'critical':
                self.alert_manager.send_alert(
                    title="Processing Aborted",
                    message="System health check failed",
                    level=AlertLevel.CRITICAL,
                    details={'issues': health_status['issues']}
                )
                return {"status": "aborted", "reason": "health_check_failed"}
            
            # Get file list
            json_files = self._get_json_files(timeframe, date)
            
            # Start monitoring
            self.monitor.start_processing(len(json_files), timeframe, date)
            
            # Process files
            result = super().process_timeframe_batch(timeframe, date)
            
            # End monitoring
            self.monitor.end_processing(result.get('status', 'completed'))
            
            # Save processing history
            self._save_processing_history(result)
            
            return result
            
        except Exception as e:
            self.monitor.critical_error(
                f"Batch processing failed: {str(e)}",
                context={'timeframe': timeframe, 'date': date}
            )
            raise
    
    def _process_single_json(self, file_path: str, timeframe: str, date: str) -> Dict:
        """Process single file with monitoring"""
        symbol = self._extract_symbol_from_filename(file_path)
        
        try:
            result = super()._process_single_json(file_path, timeframe, date)
            
            # Track result
            self.monitor.file_processed(
                symbol=symbol,
                success=result['success'],
                error=result.get('error')
            )
            
            return result
            
        except Exception as e:
            self.monitor.file_processed(
                symbol=symbol,
                success=False,
                error=str(e)
            )
            raise
    
    def _validate_json_structure(self, json_data: Dict) -> bool:
        """Validate JSON with detailed error reporting"""
        validation_errors = []
        
        # Check basic structure
        if 'chart' not in json_data or 'prices' not in json_data['chart']:
            validation_errors.append("Missing chart.prices structure")
            
        # Check price data
        if 'chart' in json_data and 'prices' in json_data['chart']:
            prices = json_data['chart']['prices']
            if not prices:
                validation_errors.append("Empty price data")
            else:
                # Check required fields
                required_fields = self.config['validation']['required_fields']['prices']
                missing_fields = []
                
                for field in required_fields:
                    if field not in prices[0]:
                        missing_fields.append(field)
                
                if missing_fields:
                    validation_errors.append(f"Missing fields: {', '.join(missing_fields)}")
        
        # Report validation errors
        if validation_errors:
            symbol = json_data.get('peripheralData', {}).get('symbol', 'unknown')
            self.monitor.validation_error(symbol, validation_errors)
            return False
        
        return True
    
    def _save_processing_history(self, result: Dict):
        """Save processing history for monitoring"""
        history_file = Path('logs/processing_history.json')
        
        # Load existing history
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
        else:
            history = []
        
        # Add new entry
        history.append({
            'timestamp': result.get('timestamp', datetime.now().isoformat()),
            'timeframe': result.get('timeframe'),
            'date': result.get('date'),
            'status': result.get('status'),
            'total_files': result.get('total_files', 0),
            'processed': result.get('processed', 0),
            'errors': result.get('errors', 0),
            'success_rate': result.get('success_rate', 0)
        })
        
        # Keep only last 100 entries
        history = history[-100:]
        
        # Save updated history
        history_file.parent.mkdir(exist_ok=True)
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)

def run_monitored_batch(timeframe: str, date: str):
    """Run batch processing with monitoring"""
    processor = MonitoredBatchProcessor()
    return processor.process_timeframe_batch(timeframe, date)