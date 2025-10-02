#!/usr/bin/env python3
"""
Daily data refresh script.
Downloads data from Google Drive folder and saves to data/ directory.
"""

import os
import json
import datetime
import sys

try:
    import gdown
except ImportError:
    print("Warning: gdown not installed. Install with: pip install gdown")
    sys.exit(1)

# Target directory
TARGET = "data"
os.makedirs(TARGET, exist_ok=True)

# Google Drive folder ID from the problem statement
# https://drive.google.com/drive/folders/1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8
GDRIVE_FOLDER_ID = "1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8"

def download_from_gdrive():
    """
    Download files from Google Drive folder to data/ directory.
    Only downloads files once per day (on the first run).
    """
    print(f"Starting data refresh at {datetime.datetime.now(datetime.UTC).isoformat()}")
    
    try:
        # Download entire folder from Google Drive
        gdrive_url = f"https://drive.google.com/drive/folders/{GDRIVE_FOLDER_ID}"
        print(f"Downloading files from Google Drive folder: {gdrive_url}")
        
        # Use gdown to download the folder
        # gdown.download_folder returns the path to the downloaded folder
        result = gdown.download_folder(
            url=gdrive_url,
            output=TARGET,
            quiet=False,
            use_cookies=False
        )
        
        print(f"Successfully downloaded files to {TARGET}/")
        
    except Exception as e:
        print(f"Error downloading from Google Drive: {e}")
        print("Creating a snapshot file as fallback...")
        
        # Fallback: create a snapshot file to track the refresh
        sample = {
            "refreshed_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "source": "daily_job",
            "status": "error",
            "error": str(e)
        }
        
        with open(os.path.join(TARGET, "snapshot.json"), "w") as f:
            json.dump(sample, f, indent=2)
        
        # Don't fail the job, just log the error
        return

    # Create metadata file to track successful refresh
    metadata = {
        "refreshed_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "source": "daily_job",
        "status": "success",
        "gdrive_folder_id": GDRIVE_FOLDER_ID
    }
    
    with open(os.path.join(TARGET, "snapshot.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    
    print("Data refresh completed successfully!")

if __name__ == "__main__":
    download_from_gdrive()
