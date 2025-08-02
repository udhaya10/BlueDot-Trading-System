#!/usr/bin/env python3
"""
Health check system for monitoring pipeline status
"""

import os
import json
import psutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class HealthChecker:
    """Monitor system health and pipeline status"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def get_system_health(self) -> Dict:
        """Get overall system health metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',  # Will be updated based on checks
            'system': self._get_system_metrics(),
            'storage': self._get_storage_metrics(),
            'pipeline': self._get_pipeline_status(),
            'data_quality': self._get_data_quality_metrics()
        }
    
    def _get_system_metrics(self) -> Dict:
        """Get system resource metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'process_count': len(psutil.pids())
        }
    
    def _get_storage_metrics(self) -> Dict:
        """Get storage metrics for data directories"""
        input_path = Path(self.config.get('data_sources', {}).get('input_path', 'data/raw'))
        output_path = Path(self.config.get('data_sources', {}).get('output_path', 'data/processed'))
        
        metrics = {
            'input_files': 0,
            'output_files': 0,
            'input_size_mb': 0,
            'output_size_mb': 0
        }
        
        # Count files and calculate sizes
        if input_path.exists():
            input_files = list(input_path.rglob('*.json'))
            metrics['input_files'] = len(input_files)
            metrics['input_size_mb'] = sum(f.stat().st_size for f in input_files) / (1024 * 1024)
        
        if output_path.exists():
            output_files = list(output_path.rglob('*.csv'))
            metrics['output_files'] = len(output_files)
            metrics['output_size_mb'] = sum(f.stat().st_size for f in output_files) / (1024 * 1024)
        
        return metrics
    
    def _get_pipeline_status(self) -> Dict:
        """Get pipeline processing status"""
        # Check last processing time
        log_path = Path('logs/processing_history.json')
        
        if log_path.exists():
            with open(log_path, 'r') as f:
                history = json.load(f)
                
            if history:
                last_run = history[-1]
                last_run_time = datetime.fromisoformat(last_run['timestamp'])
                time_since_last = datetime.now() - last_run_time
                
                return {
                    'last_run': last_run_time.isoformat(),
                    'time_since_last_hours': time_since_last.total_seconds() / 3600,
                    'last_status': last_run.get('status', 'unknown'),
                    'last_success_rate': last_run.get('success_rate', 0)
                }
        
        return {
            'last_run': None,
            'time_since_last_hours': None,
            'last_status': 'no_history',
            'last_success_rate': 0
        }
    
    def _get_data_quality_metrics(self) -> Dict:
        """Get data quality metrics from recent processing"""
        metrics_file = Path('logs/data_quality_metrics.json')
        
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                return json.load(f)
        
        return {
            'avg_completeness': 0,
            'validation_pass_rate': 0,
            'data_freshness_hours': None
        }
    
    def check_critical_issues(self) -> List[Dict]:
        """Check for critical issues that need immediate attention"""
        issues = []
        health = self.get_system_health()
        
        # Check system resources
        if health['system']['cpu_percent'] > 90:
            issues.append({
                'type': 'high_cpu',
                'severity': 'warning',
                'message': f"CPU usage is {health['system']['cpu_percent']}%"
            })
        
        if health['system']['memory_percent'] > 85:
            issues.append({
                'type': 'high_memory',
                'severity': 'warning',
                'message': f"Memory usage is {health['system']['memory_percent']}%"
            })
        
        if health['system']['disk_usage_percent'] > 80:
            issues.append({
                'type': 'high_disk',
                'severity': 'critical',
                'message': f"Disk usage is {health['system']['disk_usage_percent']}%"
            })
        
        # Check pipeline status
        if health['pipeline']['time_since_last_hours'] and health['pipeline']['time_since_last_hours'] > 26:
            issues.append({
                'type': 'stale_pipeline',
                'severity': 'warning',
                'message': f"No processing in {health['pipeline']['time_since_last_hours']:.1f} hours"
            })
        
        # Check data quality
        if health['data_quality']['validation_pass_rate'] < 90:
            issues.append({
                'type': 'low_quality',
                'severity': 'warning',
                'message': f"Validation pass rate is {health['data_quality']['validation_pass_rate']}%"
            })
        
        return issues

class HealthCheckAPI:
    """Simple API endpoint for health checks"""
    
    def __init__(self, health_checker: HealthChecker):
        self.health_checker = health_checker
    
    def get_health_status(self) -> Dict:
        """Get health status for monitoring tools"""
        health = self.health_checker.get_system_health()
        issues = self.health_checker.check_critical_issues()
        
        # Determine overall status
        if any(issue['severity'] == 'critical' for issue in issues):
            status = 'critical'
        elif any(issue['severity'] == 'warning' for issue in issues):
            status = 'warning'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'timestamp': health['timestamp'],
            'issues': issues,
            'metrics': health
        }
    
    def get_simple_status(self) -> Dict:
        """Get simple status for basic monitoring"""
        status = self.get_health_status()
        return {
            'status': status['status'],
            'healthy': status['status'] == 'healthy',
            'issue_count': len(status['issues'])
        }