#!/usr/bin/env python3
"""Test blue dot processing with matching dates"""

import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from batch_processing.batch_processor import BatchProcessor
from datetime import datetime

# Create test data with matching dates
test_data = {
    "chart": {
        "prices": [
            {"priceDate": 1753986600000, "open": 100, "high": 102, "low": 99, "close": 101, "volume": 1000000, "rlst": 75, "bc": 25.5},
            {"priceDate": 1753900200000, "open": 101, "high": 103, "low": 100, "close": 102, "volume": 1100000, "rlst": 76, "bc": 26.0},
            {"priceDate": 1753813800000, "open": 102, "high": 104, "low": 101, "close": 103, "volume": 1200000, "rlst": 77, "bc": 26.5},
        ]
    },
    "blueDotData": {
        "dates": [
            {"blueDotDate": "2025-07-31"},  # Matches first price date
            {"blueDotDate": "2025-07-29"},  # Matches third price date
            {"blueDotDate": "2024-11-11"},  # Doesn't match
        ]
    }
}

# Show what dates we're testing
print("Price dates:")
for price in test_data['chart']['prices']:
    dt = datetime.fromtimestamp(price['priceDate'] / 1000)
    print(f"  {dt.strftime('%Y-%m-%d')}")

print("\nBlue dot dates:")
for bd in test_data['blueDotData']['dates']:
    print(f"  {bd['blueDotDate']}")

# Process the data
processor = BatchProcessor()
result = processor._generate_blue_dot_signals(
    test_data['blueDotData'], 
    test_data['chart']['prices']
)

print("\nBlue dot signals:")
print("timestamp,open,high,low,close,volume")
for row in result:
    print(','.join(map(str, row)))
    # Show which date this is
    if row[4] == 1:
        print(f"  ^ Blue dot signal on this date!")