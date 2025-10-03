"""
Google Drive OAuth Integration for File Ingestion
"""
import io
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger("abaco_core.ingestion.drive")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def _creds(token_path: Path, client_secret_path: Path) -> "Credentials":
    """
    Get or refresh Google Drive credentials.
    
    Args:
        token_path: Path to token.json file
        client_secret_path: Path to client_secret.json file
    
    Returns:
        Credentials object
    """
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        raise ImportError(
            "Google Drive integration requires: pip install google-api-python-client "
            "google-auth-oauthlib google-auth"
        )
    
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")
    
    return creds


def download_folder(
    folder_id: str,
    out_dir: Path,
    client_secret_json: Path = Path("./client_secret.json"),
    token_json: Path = Path("./token.json"),
) -> List[Path]:
    """
    Downloads all files from a private Google Drive folder with user OAuth.
    First run opens a browser window for consent; token cached for future runs.
    
    Args:
        folder_id: Google Drive folder ID
        out_dir: Output directory for downloaded files
        client_secret_json: Path to client_secret.json (OAuth client config)
        token_json: Path to token.json (cached credentials)
    
    Returns:
        List of downloaded file paths
    
    Example:
        >>> from pathlib import Path
        >>> from abaco_core.ingestion.google_drive import download_folder
        >>> 
        >>> download_folder(
        ...     folder_id="1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8",
        ...     out_dir=Path("./abaco_runtime/drive_sync"),
        ...     client_secret_json=Path("./client_secret.json")
        ... )
    """
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseDownload
    except ImportError:
        raise ImportError(
            "Google Drive integration requires: pip install google-api-python-client "
            "google-auth-oauthlib google-auth"
        )
    
    out_dir.mkdir(parents=True, exist_ok=True)
    creds = _creds(token_json, client_secret_json)
    service = build("drive", "v3", credentials=creds)
    
    files = []
    page_token = None
    q = f"'{folder_id}' in parents and trashed=false"
    
    while True:
        resp = service.files().list(
            q=q,
            spaces="drive",
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token,
        ).execute()
        
        for f in resp.get("files", []):
            file_id = f["id"]
            name = f["name"]
            
            # Skip folders
            if f["mimeType"] == "application/vnd.google-apps.folder":
                continue
            
            # Download file
            request = service.files().get_media(fileId=file_id)
            fn = out_dir / name
            fh = io.FileIO(fn, "wb")
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            files.append(fn)
            logger.info(f"Downloaded {fn}")
        
        page_token = resp.get("nextPageToken", None)
        if page_token is None:
            break
    
    return files
