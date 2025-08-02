#!/usr/bin/env python3
"""
Fetch stock data from MarketSmith India API and save to Google Drive
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import time
from typing import List, Dict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarketSmithFetcher:
    def __init__(self, ms_auth_token: str):
        self.base_url = "https://marketsmithindia.com/gateway/simple-api/ms-india/instr/0"
        self.ms_auth = ms_auth_token
        self.session = requests.Session()
        
    def fetch_stock_data(self, symbol: str, instrument_id: str, start_date: str = None, end_date: str = None) -> Dict:
        """
        Fetch stock data for a given symbol
        
        Args:
            symbol: Stock symbol (e.g., 'KAYNES')
            instrument_id: MarketSmith instrument ID (e.g., '3182330')
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format
        """
        if not start_date:
            # Default to 6 months ago
            start = datetime.now() - timedelta(days=180)
            start_date = start.strftime('%Y%m%d')
            
        if not end_date:
            # Default to today
            end_date = datetime.now().strftime('%Y%m%d')
            
        url = f"{self.base_url}/{instrument_id}/details.json"
        params = {
            'symbol': symbol,
            'p': '0',
            's': start_date,
            'e': end_date,
            'b': '0INNSE50',
            'ie': '0',
            'iq': '0',
            'rs': 'N',
            'em': '0',
            'ms-auth': self.ms_auth
        }
        
        logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def save_to_file(self, data: Dict, symbol: str, output_dir: str, timeframe: str = 'daily'):
        """Save fetched data to JSON file"""
        if not data:
            return None
            
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"{symbol}_{timeframe}.json"
        file_path = output_path / filename
        
        # Save JSON
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Saved {symbol} data to {file_path}")
        return file_path
    
    def fetch_multiple_stocks(self, stock_list: List[Dict[str, str]], output_dir: str, delay: float = 1.0):
        """
        Fetch data for multiple stocks
        
        Args:
            stock_list: List of dicts with 'symbol' and 'instrument_id'
            output_dir: Directory to save JSON files
            delay: Delay between requests in seconds
        """
        results = []
        
        for i, stock in enumerate(stock_list):
            symbol = stock['symbol']
            instrument_id = stock['instrument_id']
            
            logger.info(f"Processing {i+1}/{len(stock_list)}: {symbol}")
            
            # Fetch data
            data = self.fetch_stock_data(symbol, instrument_id)
            
            if data:
                # Check if it has blue dot data
                has_blue_dots = bool(data.get('chart', {}).get('blueDotData', {}).get('dates'))
                
                # Save to file
                file_path = self.save_to_file(data, symbol, output_dir)
                
                results.append({
                    'symbol': symbol,
                    'status': 'success',
                    'file': str(file_path),
                    'has_blue_dots': has_blue_dots
                })
            else:
                results.append({
                    'symbol': symbol,
                    'status': 'failed',
                    'file': None,
                    'has_blue_dots': False
                })
            
            # Rate limiting
            if i < len(stock_list) - 1:
                time.sleep(delay)
        
        return results


def main():
    """Example usage"""
    # Configuration
    MS_AUTH = "3990+MarketSmithINDUID-Web0000000000+MarketSmithINDUID-Web0000000000+0+251509210810+-1548267953"
    
    # Stock list - Add more stocks here
    STOCK_LIST = [
        {'symbol': 'KAYNES', 'instrument_id': '3182330'},
        # Add more stocks as needed
        # {'symbol': 'TCS', 'instrument_id': 'XXXXXX'},
        # {'symbol': 'INFY', 'instrument_id': 'XXXXXX'},
    ]
    
    # Output directory
    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = f"data/marketsmith/{today}"
    
    # Create fetcher
    fetcher = MarketSmithFetcher(MS_AUTH)
    
    # Fetch all stocks
    results = fetcher.fetch_multiple_stocks(STOCK_LIST, output_dir)
    
    # Summary
    print("\n=== Fetch Summary ===")
    success_count = sum(1 for r in results if r['status'] == 'success')
    blue_dot_count = sum(1 for r in results if r['has_blue_dots'])
    
    print(f"Total stocks: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    print(f"With Blue Dots: {blue_dot_count}")
    
    print("\n=== Details ===")
    for result in results:
        status = "✓" if result['status'] == 'success' else "✗"
        dots = "●" if result['has_blue_dots'] else "○"
        print(f"{status} {dots} {result['symbol']}")


if __name__ == "__main__":
    main()