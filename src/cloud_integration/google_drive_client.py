#!/usr/bin/env python3
"""
BlueDot Trading System - Google Drive Integration
Handles downloading JSON files from Google Drive
"""

import os
import io
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import zipfile
import requests

class GoogleDriveClient:
    """Google Drive API client for downloading JSON batches"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/drive/v3"
        self.logger = logging.getLogger(__name__)
        
    def download_timeframe_batch(self, timeframe: str, date: str, 
                                folder_id: str, output_dir: str) -> Dict:
        """
        Download all JSON files for a specific timeframe and date
        
        Args:
            timeframe: 'daily' or 'weekly'
            date: Date string (YYYY-MM-DD for daily, YYYY-WXX for weekly)
            folder_id: Google Drive folder ID
            output_dir: Local directory to save files
            
        Returns:
            Dictionary with download statistics
        """
        self.logger.info(f"Starting download: {timeframe}/{date} from folder {folder_id}")
        
        try:
            # Create output directory
            output_path = Path(output_dir) / timeframe / date
            output_path.mkdir(parents=True, exist_ok=True)
            
            # List files in the specified folder
            files = self._list_files_in_folder(f"{folder_id}/{timeframe}/{date}")
            
            if not files:
                self.logger.warning(f"No files found in {timeframe}/{date}")
                return {"status": "no_files", "downloaded": 0, "errors": 0}
            
            self.logger.info(f"Found {len(files)} files to download")
            
            # Download each file
            downloaded = 0
            errors = 0
            
            for file_info in files:
                try:
                    if file_info['name'].endswith('.json'):
                        success = self._download_file(
                            file_info['id'], 
                            file_info['name'], 
                            output_path
                        )
                        if success:
                            downloaded += 1
                        else:
                            errors += 1
                    else:
                        self.logger.debug(f"Skipping non-JSON file: {file_info['name']}")
                        
                except Exception as e:
                    self.logger.error(f"Error downloading {file_info['name']}: {str(e)}")
                    errors += 1
            
            stats = {
                "status": "completed",
                "timeframe": timeframe,
                "date": date,
                "total_files": len(files),
                "downloaded": downloaded,
                "errors": errors,
                "success_rate": (downloaded / len(files)) * 100 if files else 0
            }
            
            self.logger.info(f"Download completed: {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to download batch: {str(e)}")
            return {"status": "error", "error": str(e), "downloaded": 0, "errors": 1}
    
    def _list_files_in_folder(self, folder_path: str) -> List[Dict]:
        """List all files in a Google Drive folder"""
        try:
            # For this example, we'll assume folder structure exists
            # In practice, you'd need to navigate the folder hierarchy
            
            # This is a simplified implementation
            # You would need to implement proper folder navigation
            url = f"{self.base_url}/files"
            params = {
                'key': self.api_key,
                'q': f"parents in '{folder_path}'",
                'fields': 'files(id,name,size,modifiedTime)'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('files', [])
            
        except Exception as e:
            self.logger.error(f"Failed to list files: {str(e)}")
            return []
    
    def _download_file(self, file_id: str, filename: str, output_dir: Path) -> bool:
        """Download a single file from Google Drive"""
        try:
            url = f"{self.base_url}/files/{file_id}"
            params = {
                'key': self.api_key,
                'alt': 'media'
            }
            
            response = requests.get(url, params=params, stream=True)
            response.raise_for_status()
            
            file_path = output_dir / filename
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.debug(f"Downloaded: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download {filename}: {str(e)}")
            return False
    
    def check_for_trigger_file(self, folder_id: str, timeframe: str) -> Optional[str]:
        """
        Check if trigger file exists indicating new data is ready
        
        Args:
            folder_id: Google Drive folder ID
            timeframe: 'daily' or 'weekly'
            
        Returns:
            Date string if trigger found, None otherwise
        """
        try:
            trigger_filename = f"{timeframe}_ready.txt"
            
            # List files in triggers folder
            files = self._list_files_in_folder(f"{folder_id}/triggers")
            
            for file_info in files:
                if file_info['name'] == trigger_filename:
                    # Read trigger file content to get date
                    content = self._download_file_content(file_info['id'])
                    if content:
                        # Extract date from trigger file content
                        date = content.strip()
                        self.logger.info(f"Found trigger for {timeframe}: {date}")
                        return date
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to check trigger file: {str(e)}")
            return None
    
    def _download_file_content(self, file_id: str) -> Optional[str]:
        """Download file content as string"""
        try:
            url = f"{self.base_url}/files/{file_id}"
            params = {
                'key': self.api_key,
                'alt': 'media'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Failed to download file content: {str(e)}")
            return None


class GoogleDriveUploader:
    """Helper class for uploading trigger files and status updates"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
    
    def upload_processing_status(self, folder_id: str, timeframe: str, 
                               status: Dict) -> bool:
        """Upload processing status to Google Drive"""
        try:
            # Create status filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timeframe}_status_{timestamp}.json"
            
            # This would require Google Drive upload API implementation
            # For now, just log the status
            self.logger.info(f"Status to upload: {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to upload status: {str(e)}")
            return False


# Utility functions for GitHub Actions
def download_daily_data():
    """Entry point for daily data download"""
    import os
    
    api_key = os.getenv('GOOGLE_DRIVE_API_KEY')
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    if not api_key or not folder_id:
        print("❌ Missing Google Drive credentials")
        return
    
    client = GoogleDriveClient(api_key)
    
    # Check for trigger file first
    date = client.check_for_trigger_file(folder_id, 'daily')
    if not date:
        print("ℹ️ No daily trigger file found, using today's date")
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Download data
    result = client.download_timeframe_batch(
        timeframe='daily',
        date=date,
        folder_id=folder_id,
        output_dir='data/raw'
    )
    
    print(f"📊 Download result: {result}")


def download_weekly_data():
    """Entry point for weekly data download"""
    import os
    
    api_key = os.getenv('GOOGLE_DRIVE_API_KEY')
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    if not api_key or folder_id:
        print("❌ Missing Google Drive credentials")
        return
    
    client = GoogleDriveClient(api_key)
    
    # Check for trigger file first
    date = client.check_for_trigger_file(folder_id, 'weekly')
    if not date:
        print("ℹ️ No weekly trigger file found, using current week")
        # Calculate current week (YYYY-WXX format)
        now = datetime.now()
        week_num = now.isocalendar()[1]
        date = f"{now.year}-W{week_num:02d}"
    
    # Download data
    result = client.download_timeframe_batch(
        timeframe='weekly',
        date=date,
        folder_id=folder_id,
        output_dir='data/raw'
    )
    
    print(f"📊 Download result: {result}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "daily":
            download_daily_data()
        elif sys.argv[1] == "weekly":
            download_weekly_data()
        else:
            print("Usage: python google_drive_client.py [daily|weekly]")
    else:
        print("Usage: python google_drive_client.py [daily|weekly]")