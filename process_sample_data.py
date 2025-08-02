#!/usr/bin/env python3
"""Process sample data files to test the conversion pipeline"""

import os
import json
import pandas as pd
from datetime import datetime
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def process_sample_json(input_file, output_dir):
    """Process a single JSON file and generate CSV outputs"""
    
    print(f"\n📄 Processing: {os.path.basename(input_file)}")
    
    # Read JSON data
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Extract symbol from filename or use default
    filename = os.path.basename(input_file)
    symbol = filename.replace('_daily_data.json', '').replace('_stock_data.json', '').replace('sample_', 'SAMPLE').upper()
    
    # Extract price data
    if 'chart' in data and 'prices' in data['chart']:
        prices = data['chart']['prices']
        print(f"  Found {len(prices)} price records")
        
        # Convert to DataFrame
        df = pd.DataFrame(prices)
        
        # Convert timestamp to TradingView format
        df['timestamp'] = pd.to_datetime(df['priceDate'], unit='ms').dt.strftime('%Y%m%dT%H%M')
        
        # 1. Price Data CSV
        price_csv = os.path.join(output_dir, f"{symbol}_PRICE_DATA.csv")
        price_df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].copy()
        price_df.to_csv(price_csv, index=False, header=False)
        print(f"  ✅ Created: {os.path.basename(price_csv)}")
        
        # 2. RLST Rating CSV
        if 'rlst' in df.columns:
            rlst_csv = os.path.join(output_dir, f"{symbol}_RLST_RATING.csv")
            rlst_df = df[['timestamp', 'rlst', 'rlst', 'rlst', 'rlst', 'volume']].copy()
            rlst_df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            rlst_df.to_csv(rlst_csv, index=False, header=False)
            print(f"  ✅ Created: {os.path.basename(rlst_csv)}")
        
        # 3. BC Indicator CSV
        if 'bc' in df.columns:
            bc_csv = os.path.join(output_dir, f"{symbol}_BC_INDICATOR.csv")
            bc_df = df[['timestamp', 'bc', 'bc', 'bc', 'bc', 'volume']].copy()
            bc_df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            bc_df.to_csv(bc_csv, index=False, header=False)
            print(f"  ✅ Created: {os.path.basename(bc_csv)}")
    
    # Extract blue dot data
    if 'blueDotData' in data and 'dates' in data['blueDotData']:
        blue_dots = data['blueDotData']['dates']
        print(f"  Found {len(blue_dots)} blue dot signals")
        
        if prices and blue_dots:
            # Create a DataFrame with all dates from price data
            df_price = pd.DataFrame(prices)
            df_price['timestamp'] = pd.to_datetime(df_price['priceDate'], unit='ms').dt.strftime('%Y%m%dT%H%M')
            df_price['date'] = pd.to_datetime(df_price['priceDate'], unit='ms').dt.date
            
            # Convert blue dot dates to date objects
            blue_dot_dates = [pd.to_datetime(ts, unit='ms').date() for ts in blue_dots]
            
            # Create blue dot indicator (1 if date has blue dot, 0 otherwise)
            df_price['blue_dot'] = df_price['date'].isin(blue_dot_dates).astype(int)
            
            # 4. Blue Dots CSV
            blue_csv = os.path.join(output_dir, f"{symbol}_BLUE_DOTS.csv")
            blue_df = df_price[['timestamp', 'blue_dot', 'blue_dot', 'blue_dot', 'blue_dot', 'volume']].copy()
            blue_df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            blue_df.to_csv(blue_csv, index=False, header=False)
            print(f"  ✅ Created: {os.path.basename(blue_csv)}")
    
    # Show peripheral data if available
    if 'peripheralData' in data:
        peripheral = data['peripheralData']
        print(f"  📊 Stock Info: {peripheral.get('symbol', 'N/A')} - {peripheral.get('companyName', 'N/A')}")
        print(f"  📈 RS Rating: {peripheral.get('rsRating', 'N/A')}")

def main():
    """Process all sample data files"""
    
    print("🚀 Processing Sample Data Files")
    print("=" * 50)
    
    # Set up directories
    input_dir = "data/raw"
    output_dir = "data/output/sample"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each JSON file
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            input_file = os.path.join(input_dir, filename)
            try:
                process_sample_json(input_file, output_dir)
            except Exception as e:
                print(f"  ❌ Error processing {filename}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Sample data processing complete!")
    print(f"📁 Output files saved to: {output_dir}")
    
    # List generated files
    print("\n📊 Generated CSV files:")
    for file in sorted(os.listdir(output_dir)):
        if file.endswith('.csv'):
            file_path = os.path.join(output_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  - {file} ({file_size:,} bytes)")

if __name__ == "__main__":
    main()