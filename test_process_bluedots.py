#!/usr/bin/env python3
"""Test processing a file with blue dots"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from batch_processing.batch_processor import DataProcessor
import json

# Process the test file
processor = DataProcessor()

# Load the test file
with open('data/raw/test_with_bluedots.json', 'r') as f:
    json_data = json.load(f)

# Process it
output = processor.process_json(json_data, 'TESTSTOCK')

# Check blue dots output
if 'BLUE_DOTS' in output:
    print("Blue Dots CSV Output:")
    print("timestamp,open,high,low,close,volume")
    for row in output['BLUE_DOTS'][:10]:  # Show first 10 rows
        print(','.join(map(str, row)))
else:
    print("No blue dots output generated")