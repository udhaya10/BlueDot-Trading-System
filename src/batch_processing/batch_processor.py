#!/usr/bin/env python3
"""
BlueDot Trading System - Batch Processor
Handles processing of 1000+ JSON files for daily/weekly timeframes
"""

import os
import json
import logging
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import pandas as pd
import yaml

class BatchProcessor:
    """Main batch processing engine for multiple JSON files"""
    
    def __init__(self, config_path: str = "config/data_config.yaml"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format=self.config['logging']['format']
        )
        return logging.getLogger(__name__)
    
    def process_timeframe_batch(self, timeframe: str, date: str) -> Dict:
        """
        Process all JSON files for a specific timeframe and date
        
        Args:
            timeframe: 'daily' or 'weekly'
            date: Date string (YYYY-MM-DD for daily, YYYY-WXX for weekly)
            
        Returns:
            Dictionary with processing statistics
        """
        self.logger.info(f"Starting {timeframe} batch processing for {date}")
        
        # Get list of JSON files to process
        json_files = self._get_json_files(timeframe, date)
        self.logger.info(f"Found {len(json_files)} JSON files to process")
        
        if not json_files:
            self.logger.warning(f"No JSON files found for {timeframe}/{date}")
            return {"status": "no_files", "processed": 0, "errors": 0}
        
        # Process files in batches
        batch_size = self.config['data_sources']['batch_processing']['max_files_per_batch']
        total_processed = 0
        total_errors = 0
        
        for i in range(0, len(json_files), batch_size):
            batch = json_files[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} files")
            
            batch_results = self._process_batch_parallel(batch, timeframe, date)
            total_processed += batch_results['processed']
            total_errors += batch_results['errors']
        
        # Generate summary statistics
        stats = {
            "status": "completed",
            "timeframe": timeframe,
            "date": date,
            "total_files": len(json_files),
            "processed": total_processed,
            "errors": total_errors,
            "success_rate": (total_processed / len(json_files)) * 100 if json_files else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"Batch processing completed: {stats}")
        return stats
    
    def _get_json_files(self, timeframe: str, date: str) -> List[str]:
        """Get list of JSON files for processing"""
        input_path = Path(self.config['data_sources']['input_path'])
        
        # Look for files in timeframe/date directory
        batch_dir = input_path / timeframe / date
        
        if not batch_dir.exists():
            self.logger.warning(f"Batch directory not found: {batch_dir}")
            return []
        
        json_files = list(batch_dir.glob("*.json"))
        return [str(f) for f in json_files]
    
    def _process_batch_parallel(self, json_files: List[str], timeframe: str, date: str) -> Dict:
        """Process a batch of JSON files in parallel"""
        max_workers = self.config['data_sources']['batch_processing']['parallel_workers']
        processed = 0
        errors = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all files for processing
            future_to_file = {
                executor.submit(self._process_single_json, file_path, timeframe, date): file_path
                for file_path in json_files
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result['success']:
                        processed += 1
                    else:
                        errors += 1
                        self.logger.error(f"Failed to process {file_path}: {result['error']}")
                except Exception as e:
                    errors += 1
                    self.logger.error(f"Exception processing {file_path}: {str(e)}")
        
        return {"processed": processed, "errors": errors}
    
    def _process_single_json(self, file_path: str, timeframe: str, date: str) -> Dict:
        """
        Process a single JSON file and generate CSV outputs
        
        Args:
            file_path: Path to JSON file
            timeframe: 'daily' or 'weekly'
            date: Date string
            
        Returns:
            Dictionary with processing result
        """
        try:
            # Extract stock symbol from filename
            symbol = self._extract_symbol_from_filename(file_path)
            
            # Load and validate JSON data
            with open(file_path, 'r') as f:
                json_data = json.load(f)
            
            # Log JSON structure
            self.logger.info(f"JSON top-level keys: {list(json_data.keys())}")
            if 'chart' in json_data:
                self.logger.info(f"Chart keys: {list(json_data['chart'].keys())}")
            
            # Validate JSON structure
            if not self._validate_json_structure(json_data):
                return {"success": False, "error": "Invalid JSON structure"}
            
            # Process different data streams
            csv_outputs = self._generate_csv_data(json_data, symbol, timeframe)
            
            # Save CSV files
            self._save_csv_files(csv_outputs, symbol, timeframe, date)
            
            return {"success": True, "symbol": symbol, "csvs_generated": len(csv_outputs)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_symbol_from_filename(self, file_path: str) -> str:
        """Extract stock symbol from filename"""
        filename = Path(file_path).name
        # Assume format: SYMBOL_timeframe.json (e.g., AAPL_daily.json)
        symbol = filename.split('_')[0]
        return symbol
    
    def _validate_json_structure(self, json_data: Dict) -> bool:
        """Validate JSON data structure"""
        required_fields = self.config['validation']['required_fields']
        
        # Check chart.prices structure
        if 'chart' not in json_data or 'prices' not in json_data['chart']:
            return False
        
        # Check if we have price data
        prices = json_data['chart']['prices']
        if not prices or len(prices) == 0:
            return False
        
        # Check required fields in price data
        price_fields = required_fields['prices']
        for price_record in prices[:3]:  # Check first 3 records
            for field in price_fields:
                if field not in price_record:
                    return False
        
        # Check blueDotData structure
        if 'blueDotData' in json_data.get('chart', {}):
            if 'dates' not in json_data['chart']['blueDotData']:
                return False
        
        return True
    
    def _generate_csv_data(self, json_data: Dict, symbol: str, timeframe: str) -> Dict[str, List]:
        """Generate CSV data for all output files"""
        csv_outputs = {
            'PRICE_DATA': [],
            'RLST_RATING': [],
            'BC_INDICATOR': [],
            'BLUE_DOTS': []
        }
        
        # Process price data (OHLCV + RLST + BC)
        if 'chart' not in json_data:
            self.logger.error("No 'chart' key in JSON data")
            return csv_outputs
            
        if 'prices' not in json_data['chart']:
            self.logger.error("No 'prices' key in chart data")
            return csv_outputs
            
        prices = json_data['chart']['prices']
        self.logger.info(f"Processing {len(prices)} price records")
        
        for i, price_record in enumerate(prices):
            # Convert timestamp
            timestamp = self._convert_timestamp(price_record['priceDate'])
            
            # PRICE_DATA.csv - Standard OHLCV
            csv_outputs['PRICE_DATA'].append([
                timestamp,
                price_record.get('open', 0),
                price_record.get('high', 0),
                price_record.get('low', 0),
                price_record.get('close', 0),
                price_record.get('volume', 0)
            ])
            
            # RLST_RATING.csv - Time-aligned RLST
            csv_outputs['RLST_RATING'].append([
                timestamp,
                0,  # Open (0 for indicators)
                1000,  # High (1000 for indicators)
                0,  # Low (0 for indicators)
                price_record.get('rlst', 0),  # Close (RLST value)
                0   # Volume (0 for indicators)
            ])
            
            # BC_INDICATOR.csv - Time-aligned BC
            csv_outputs['BC_INDICATOR'].append([
                timestamp,
                0,  # Open
                1000,  # High
                0,  # Low
                price_record.get('bc', 0),  # Close (BC value)
                0   # Volume
            ])
        
        # Process blue dot signals
        blue_dot_signals = self._generate_blue_dot_signals(
            json_data.get('chart', {}).get('blueDotData', {}), 
            prices
        )
        csv_outputs['BLUE_DOTS'] = blue_dot_signals
        
        # Log the size of each CSV output
        for key, data in csv_outputs.items():
            self.logger.info(f"CSV output {key}: {len(data)} rows")
            print(f"CSV output {key}: {len(data)} rows")  # Also print to console
        
        return csv_outputs
    
    def _convert_timestamp(self, timestamp_ms: int) -> str:
        """Convert millisecond timestamp to TradingView format"""
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime("%Y%m%dT")
    
    def _generate_blue_dot_signals(self, blue_dot_data: Dict, prices: List[Dict]) -> List:
        """Generate binary blue dot signals aligned with price data"""
        signals = []
        
        # Get blue dot dates and convert to date strings for comparison
        blue_dot_dates = set()
        if 'dates' in blue_dot_data and blue_dot_data['dates']:
            # Handle both formats: list of timestamps or list of objects
            for date_item in blue_dot_data['dates']:
                if isinstance(date_item, dict) and 'blueDotDate' in date_item:
                    # Date string format (e.g., "2024-11-11")
                    blue_dot_dates.add(date_item['blueDotDate'])
                elif isinstance(date_item, (int, float)):
                    # Timestamp format - convert to date string
                    dt = datetime.fromtimestamp(date_item / 1000)
                    blue_dot_dates.add(dt.strftime('%Y-%m-%d'))
        
        # Generate signals for each price record
        for price_record in prices:
            timestamp = self._convert_timestamp(price_record['priceDate'])
            
            # Convert price timestamp to date string for comparison
            price_date = datetime.fromtimestamp(price_record['priceDate'] / 1000).strftime('%Y-%m-%d')
            
            # Check if this date has a blue dot signal
            signal_value = 1 if price_date in blue_dot_dates else 0
            
            signals.append([
                timestamp,
                0,      # Open
                1000,   # High
                0,      # Low
                signal_value,  # Close (1 for blue dot, 0 for no signal)
                0       # Volume
            ])
        
        return signals
    
    def _save_csv_files(self, csv_outputs: Dict[str, List], symbol: str, timeframe: str, date: str):
        """Save CSV files to output directory"""
        output_path = Path(self.config['data_sources']['output_path'])
        
        # Create output directory structure
        output_dir = output_path / timeframe / date
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save each CSV file
        file_configs = self.config['output']['files']
        self.logger.info(f"File configs: {file_configs}")
        self.logger.info(f"CSV outputs keys: {csv_outputs.keys()}")
        
        for data_type, file_suffix in file_configs.items():
            # Convert data_type to match CSV output keys
            if data_type == 'price_data':
                csv_key = 'PRICE_DATA'
            elif data_type == 'rlst_rating':
                csv_key = 'RLST_RATING'
            elif data_type == 'bc_indicator':
                csv_key = 'BC_INDICATOR'
            elif data_type == 'blue_dots':
                csv_key = 'BLUE_DOTS'
            else:
                continue
                
            self.logger.info(f"Processing {data_type} -> {csv_key}")
            print(f"Processing {data_type} -> {csv_key}")  # Print to console
            if csv_key in csv_outputs:
                # Generate filename: SYMBOL_FILE_TYPE.csv
                filename = f"{symbol}_{file_suffix}"
                file_path = output_dir / filename
                
                # Write CSV data
                csv_data = csv_outputs[csv_key]
                self.logger.info(f"Writing {filename} to {file_path}")
                self.logger.info(f"CSV data has {len(csv_data)} rows")
                
                with open(file_path, 'w') as f:
                    for row in csv_data:
                        f.write(','.join(map(str, row)) + '\n')
                
                # Verify file was written
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    self.logger.info(f"✓ Saved {filename} with {len(csv_data)} rows ({file_size} bytes)")
                else:
                    self.logger.error(f"✗ Failed to save {filename}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process JSON batch")
    parser.add_argument("--timeframe", required=True, choices=["daily", "weekly"])
    parser.add_argument("--date", required=True, help="Date string (YYYY-MM-DD or YYYY-WXX)")
    
    args = parser.parse_args()
    
    processor = BatchProcessor()
    result = processor.process_timeframe_batch(args.timeframe, args.date)
    
    print(f"Processing completed: {result}")