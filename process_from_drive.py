#!/usr/bin/env python3
"""Download files from Google Drive and process them"""

import os
import json
import shutil
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from dotenv import load_dotenv
import io
import subprocess
import sys

# Load environment variables
load_dotenv()

def download_files_from_drive(timeframe='daily', date_str=None):
    """Download files from Google Drive folder"""
    
    # Get credentials and folder IDs
    service_account_file = os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT')
    folder_id = os.getenv(f'{timeframe.upper()}_FOLDER_ID')
    
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    print(f"📥 Downloading {timeframe} files for {date_str}")
    
    # Create credentials
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    
    # Build the service
    service = build('drive', 'v3', credentials=credentials)
    
    # Create local directory
    local_dir = f"data/raw/{timeframe}/{date_str}"
    os.makedirs(local_dir, exist_ok=True)
    
    # List and download files
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=100,
            fields="files(id, name, size)"
        ).execute()
        
        files = results.get('files', [])
        print(f"Found {len(files)} files to download")
        
        downloaded = 0
        for file in files:
            if file['name'].endswith('.json'):
                print(f"  Downloading: {file['name']}")
                
                # Download file
                request = service.files().get_media(fileId=file['id'])
                file_path = os.path.join(local_dir, file['name'])
                
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                
                # Write to file
                with open(file_path, 'wb') as f:
                    f.write(fh.getvalue())
                
                downloaded += 1
                print(f"    ✅ Saved to: {file_path}")
        
        print(f"\n✅ Downloaded {downloaded} files to {local_dir}")
        return local_dir, downloaded
        
    except Exception as e:
        print(f"❌ Error downloading files: {e}")
        return None, 0

def process_batch(timeframe='daily', date_str=None):
    """Run the batch processor"""
    
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n🔄 Processing {timeframe} batch for {date_str}")
    
    # Run batch processor
    cmd = [
        sys.executable,
        'src/batch_processing/batch_processor.py',
        '--timeframe', timeframe,
        '--date', date_str
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Batch processing completed successfully")
        print(result.stdout)
    else:
        print("❌ Batch processing failed")
        print(result.stderr)
    
    return result.returncode == 0

def main():
    """Main process flow"""
    
    print("🚀 BlueDot Trading System - Google Drive Processing")
    print("=" * 60)
    
    # Process daily data
    timeframe = 'daily'
    date_str = '2024-08-02'  # Use a specific date for testing
    
    # Download files
    local_dir, count = download_files_from_drive(timeframe, date_str)
    
    if count > 0:
        # Process the batch
        success = process_batch(timeframe, date_str)
        
        if success:
            # Check output
            output_dir = f"data/output/{timeframe}/{date_str}"
            if os.path.exists(output_dir):
                csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
                print(f"\n📊 Generated {len(csv_files)} CSV files:")
                for csv in sorted(csv_files)[:10]:  # Show first 10
                    print(f"  - {csv}")
                if len(csv_files) > 10:
                    print(f"  ... and {len(csv_files) - 10} more files")
    else:
        print("\n⚠️ No files to process")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()