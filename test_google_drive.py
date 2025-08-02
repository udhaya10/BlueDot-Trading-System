#!/usr/bin/env python3
"""Test Google Drive connection with service account"""

import os
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_drive_connection():
    """Test the Google Drive API connection"""
    
    # Get credentials path from environment
    service_account_file = os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT')
    daily_folder_id = os.getenv('DAILY_FOLDER_ID')
    weekly_folder_id = os.getenv('WEEKLY_FOLDER_ID')
    
    print("🔍 Testing Google Drive Connection...")
    print(f"Service Account File: {service_account_file}")
    print(f"Daily Folder ID: {daily_folder_id}")
    print(f"Weekly Folder ID: {weekly_folder_id}")
    print("-" * 50)
    
    # Check if service account file exists
    if not os.path.exists(service_account_file):
        print("❌ Error: Service account file not found!")
        return False
    
    try:
        # Create credentials
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        
        # Build the service
        service = build('drive', 'v3', credentials=credentials)
        
        print("✅ Successfully authenticated with Google Drive!")
        print("-" * 50)
        
        # Test access to Daily folder
        print(f"\n📁 Testing access to Daily folder...")
        try:
            daily_folder = service.files().get(
                fileId=daily_folder_id,
                fields='id, name, mimeType'
            ).execute()
            print(f"✅ Daily folder accessible: {daily_folder.get('name')}")
            
            # List first 5 files in daily folder
            results = service.files().list(
                q=f"'{daily_folder_id}' in parents",
                pageSize=5,
                fields="files(id, name)"
            ).execute()
            files = results.get('files', [])
            if files:
                print(f"   Found {len(files)} files (showing first 5):")
                for file in files:
                    print(f"   - {file['name']}")
            else:
                print("   No files found in Daily folder")
                
        except HttpError as e:
            print(f"❌ Error accessing Daily folder: {e}")
        
        # Test access to Weekly folder
        print(f"\n📁 Testing access to Weekly folder...")
        try:
            weekly_folder = service.files().get(
                fileId=weekly_folder_id,
                fields='id, name, mimeType'
            ).execute()
            print(f"✅ Weekly folder accessible: {weekly_folder.get('name')}")
            
            # List first 5 files in weekly folder
            results = service.files().list(
                q=f"'{weekly_folder_id}' in parents",
                pageSize=5,
                fields="files(id, name)"
            ).execute()
            files = results.get('files', [])
            if files:
                print(f"   Found {len(files)} files (showing first 5):")
                for file in files:
                    print(f"   - {file['name']}")
            else:
                print("   No files found in Weekly folder")
                
        except HttpError as e:
            print(f"❌ Error accessing Weekly folder: {e}")
        
        print("\n✅ Google Drive connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Google Drive: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    # Install python-dotenv if not present
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("Installing python-dotenv...")
        os.system(f"{sys.executable} -m pip install python-dotenv")
        from dotenv import load_dotenv
    
    success = test_google_drive_connection()
    sys.exit(0 if success else 1)