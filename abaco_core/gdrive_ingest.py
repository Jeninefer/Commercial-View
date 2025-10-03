"""
Google Drive ingestion with OAuth for Commercial-View.

Local-first approach with OAuth authentication. No secrets hardcoded.
"""

import os
import json
import logging
import pickle
from pathlib import Path
from typing import Optional, List, Dict, Any
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

logger = logging.getLogger("abaco_core.gdrive_ingest")

# OAuth scopes for Google Drive readonly access
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Token storage path
TOKEN_PATH = Path.home() / ".abaco" / "gdrive_token.pickle"
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")


class GoogleDriveIngestor:
    """
    Google Drive file ingestion with OAuth.
    
    Provides local-first authentication and file download capabilities.
    Credentials and tokens are stored locally, never in source code.
    
    Example:
        >>> ingestor = GoogleDriveIngestor()
        >>> files = ingestor.list_files(folder_id="your_folder_id")
        >>> data = ingestor.download_file(file_id="your_file_id")
    """
    
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[Path] = None
    ):
        """
        Initialize Google Drive ingestor.
        
        Args:
            credentials_path: Path to credentials.json from Google Cloud Console.
                            If None, uses GOOGLE_CREDENTIALS_PATH env var.
            token_path: Path to store OAuth token. If None, uses default.
        
        Raises:
            FileNotFoundError: If credentials file not found.
        """
        self.credentials_path = credentials_path or CREDENTIALS_PATH
        self.token_path = token_path or TOKEN_PATH
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        Authenticate with Google Drive API using OAuth.
        
        Uses stored token if available, otherwise initiates OAuth flow.
        
        Raises:
            FileNotFoundError: If credentials file not found.
        """
        creds = None
        
        # Load token if it exists
        if self.token_path.exists():
            with open(self.token_path, "rb") as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired token...")
                creds.refresh(Request())
            else:
                if not Path(self.credentials_path).exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        f"Download from Google Cloud Console and set GOOGLE_CREDENTIALS_PATH"
                    )
                
                logger.info("Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token for future use
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "wb") as token:
                pickle.dump(creds, token)
            logger.info(f"Token saved to {self.token_path}")
        
        self.service = build("drive", "v3", credentials=creds)
    
    def list_files(
        self,
        folder_id: Optional[str] = None,
        mime_type: Optional[str] = None,
        name_contains: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List files in Google Drive.
        
        Args:
            folder_id: Optional folder ID to search within.
            mime_type: Optional MIME type filter (e.g., 'text/csv').
            name_contains: Optional filename substring filter.
            max_results: Maximum number of results to return.
        
        Returns:
            List of file metadata dictionaries.
        """
        query_parts = []
        
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")
        
        if mime_type:
            query_parts.append(f"mimeType='{mime_type}'")
        
        if name_contains:
            query_parts.append(f"name contains '{name_contains}'")
        
        query = " and ".join(query_parts) if query_parts else None
        
        try:
            results = self.service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, mimeType, size, modifiedTime, createdTime)"
            ).execute()
            
            files = results.get("files", [])
            logger.info(f"Found {len(files)} files")
            return files
        
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            raise
    
    def download_file(
        self,
        file_id: str,
        output_path: Optional[Path] = None
    ) -> bytes:
        """
        Download a file from Google Drive.
        
        Args:
            file_id: Google Drive file ID.
            output_path: Optional path to save file. If None, returns bytes.
        
        Returns:
            File contents as bytes.
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_data = io.BytesIO()
            downloader = MediaIoBaseDownload(file_data, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    logger.info(f"Download progress: {int(status.progress() * 100)}%")
            
            content = file_data.getvalue()
            
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(content)
                logger.info(f"File saved to {output_path}")
            
            return content
        
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            raise
    
    def download_folder(
        self,
        folder_id: str,
        output_dir: Path,
        mime_type: Optional[str] = None
    ) -> List[Path]:
        """
        Download all files from a folder.
        
        Args:
            folder_id: Google Drive folder ID.
            output_dir: Directory to save files.
            mime_type: Optional MIME type filter.
        
        Returns:
            List of downloaded file paths.
        """
        files = self.list_files(folder_id=folder_id, mime_type=mime_type)
        downloaded = []
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            file_id = file["id"]
            file_name = file["name"]
            output_path = output_dir / file_name
            
            logger.info(f"Downloading {file_name}...")
            self.download_file(file_id, output_path)
            downloaded.append(output_path)
        
        logger.info(f"Downloaded {len(downloaded)} files to {output_dir}")
        return downloaded
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific file.
        
        Args:
            file_id: Google Drive file ID.
        
        Returns:
            File metadata dictionary.
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, modifiedTime, createdTime, parents"
            ).execute()
            return file
        
        except Exception as e:
            logger.error(f"Error getting file metadata: {e}")
            raise
