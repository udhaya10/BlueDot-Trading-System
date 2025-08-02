#!/usr/bin/env python3
"""Check files in Google Drive folders"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_drive_files():
    """List files in both daily and weekly folders"""
    
    # Get credentials and folder IDs
    service_account_file = os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT')
    daily_folder_id = os.getenv('DAILY_FOLDER_ID')
    weekly_folder_id = os.getenv('WEEKLY_FOLDER_ID')
    
    # Create credentials
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    
    # Build the service
    service = build('drive', 'v3', credentials=credentials)
    
    print("🔍 Checking Google Drive Files")
    print("=" * 60)
    
    # Check Daily folder
    print("\n📁 DAILY FOLDER:")
    print("-" * 60)
    try:
        results = service.files().list(
            q=f"'{daily_folder_id}' in parents",
            pageSize=100,
            fields="files(id, name, size, modifiedTime)"
        ).execute()
        
        files = results.get('files', [])
        if files:
            print(f"Found {len(files)} files:")
            total_size = 0
            for file in sorted(files, key=lambda x: x['name']):
                size_mb = int(file.get('size', 0)) / (1024 * 1024)
                total_size += size_mb
                print(f"  📄 {file['name']:<40} {size_mb:>8.2f} MB")
            print(f"\nTotal: {len(files)} files, {total_size:.2f} MB")
        else:
            print("  No files found")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Check Weekly folder
    print("\n📁 WEEKLY FOLDER:")
    print("-" * 60)
    try:
        results = service.files().list(
            q=f"'{weekly_folder_id}' in parents",
            pageSize=100,
            fields="files(id, name, size, modifiedTime)"
        ).execute()
        
        files = results.get('files', [])
        if files:
            print(f"Found {len(files)} files:")
            total_size = 0
            for file in sorted(files, key=lambda x: x['name']):
                size_mb = int(file.get('size', 0)) / (1024 * 1024)
                total_size += size_mb
                print(f"  📄 {file['name']:<40} {size_mb:>8.2f} MB")
            print(f"\nTotal: {len(files)} files, {total_size:.2f} MB")
        else:
            print("  No files found")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    list_drive_files()