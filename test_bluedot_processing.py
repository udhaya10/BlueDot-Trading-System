#!/usr/bin/env python3
"""Test blue dot processing with sample data"""

import json
from datetime import datetime

# Sample JSON with blue dot data
sample_json = {
    "chart": {
        "prices": [
            {"priceDate": 1704067200000, "open": 100, "high": 102, "low": 99, "close": 101, "volume": 1000000, "rlst": 75, "bc": 25.5},
            {"priceDate": 1704153600000, "open": 101, "high": 103, "low": 100, "close": 102, "volume": 1100000, "rlst": 76, "bc": 26.0},
            {"priceDate": 1704240000000, "open": 102, "high": 104, "low": 101, "close": 103, "volume": 1200000, "rlst": 77, "bc": 26.5},
        ]
    },
    "blueDotData": {
        "dates": [1704067200000, 1704240000000]  # Blue dots on first and third day
    }
}

def process_blue_dots(json_data):
    """Process blue dot signals"""
    prices = json_data['chart']['prices']
    blue_dot_dates = set()
    
    # Get blue dot timestamps
    if 'blueDotData' in json_data and 'dates' in json_data['blueDotData']:
        blue_dot_dates = set(json_data['blueDotData']['dates'])
    
    # Generate signals
    signals = []
    for price in prices:
        timestamp = price['priceDate']
        has_signal = 1 if timestamp in blue_dot_dates else 0
        
        # Convert timestamp for display
        dt = datetime.fromtimestamp(timestamp / 1000)
        date_str = dt.strftime("%Y-%m-%d")
        
        signals.append({
            'date': date_str,
            'timestamp': timestamp,
            'signal': has_signal
        })
    
    return signals

# Test the processing
signals = process_blue_dots(sample_json)
print("Blue Dot Signals:")
for signal in signals:
    print(f"Date: {signal['date']}, Signal: {signal['signal']}")