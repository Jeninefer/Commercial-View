"""
Google Drive authentication and file download module.
Implements OAuth 2.0 flow for secure access to Google Drive.
"""

import os
import pickle
from pathlib import Path
from typing import Optional, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

from config import CREDENTIALS_FILE, TOKEN_FILE

# If modifying these scopes, delete the token.json file
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]


class GoogleDriveClient:
    """Client for interacting with Google Drive API."""
    
    def __init__(self):
        self.creds: Optional[Credentials] = None
        self.service = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive using OAuth 2.0.
        Returns True if authentication successful.
        """
        # Check if token file exists
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not CREDENTIALS_FILE.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found at {CREDENTIALS_FILE}. "
                        "Please download OAuth 2.0 credentials from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(self.creds, token)
        
        # Build the service
        self.service = build('drive', 'v3', credentials=self.creds)
        return True
    
    def extract_folder_id(self, folder_url: str) -> str:
        """
        Extract folder ID from Google Drive URL.
        Supports various URL formats.
        """
        if '/folders/' in folder_url:
            return folder_url.split('/folders/')[-1].split('?')[0]
        return folder_url
    
    def list_files(self, folder_id: str) -> List[dict]:
        """
        List all files in a Google Drive folder.
        Returns list of file metadata dictionaries.
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        results = []
        page_token = None
        
        while True:
            response = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType, modifiedTime, size)',
                pageToken=page_token
            ).execute()
            
            results.extend(response.get('files', []))
            page_token = response.get('nextPageToken')
            
            if not page_token:
                break
        
        return results
    
    def download_file(self, file_id: str, destination_path: Path) -> bool:
        """
        Download a file from Google Drive.
        Returns True if download successful.
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            # Write to file
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            with open(destination_path, 'wb') as f:
                fh.seek(0)
                f.write(fh.read())
            
            return True
        except Exception as e:
            print(f"Error downloading file {file_id}: {e}")
            return False
    
    def download_folder(self, folder_url: str, destination_dir: Path) -> dict:
        """
        Download all files from a Google Drive folder.
        Returns dictionary with download results.
        """
        folder_id = self.extract_folder_id(folder_url)
        files = self.list_files(folder_id)
        
        results = {
            'total': len(files),
            'successful': 0,
            'failed': 0,
            'files': []
        }
        
        for file in files:
            file_id = file['id']
            file_name = file['name']
            destination_path = destination_dir / file_name
            
            print(f"Downloading: {file_name}...")
            success = self.download_file(file_id, destination_path)
            
            if success:
                results['successful'] += 1
                results['files'].append({
                    'name': file_name,
                    'path': str(destination_path),
                    'status': 'success'
                })
            else:
                results['failed'] += 1
                results['files'].append({
                    'name': file_name,
                    'path': str(destination_path),
                    'status': 'failed'
                })
        
        return results


def download_data_from_drive(folder_url: str, output_dir: Path) -> dict:
    """
    Convenience function to download all data from Google Drive folder.
    """
    client = GoogleDriveClient()
    client.authenticate()
    return client.download_folder(folder_url, output_dir)
