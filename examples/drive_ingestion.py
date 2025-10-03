"""
Example: Google Drive Ingestion

This script demonstrates how to download files from Google Drive using OAuth.
First run will open a browser for consent; subsequent runs use cached token.
"""

from pathlib import Path
from abaco_core.ingestion.google_drive import download_folder

# Configuration
FOLDER_ID = "YOUR_GOOGLE_DRIVE_FOLDER_ID"  # Replace with actual folder ID
OUTPUT_DIR = Path("./data/drive_sync")
CLIENT_SECRET = Path("./client_secret.json")
TOKEN_FILE = Path("./token.json")

print("=" * 80)
print("GOOGLE DRIVE FILE INGESTION")
print("=" * 80)
print()

# Instructions
print("Setup Instructions:")
print("-" * 80)
print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
print("2. Create a new project or select existing one")
print("3. Enable Google Drive API")
print("4. Create OAuth 2.0 Client ID (Desktop application)")
print("5. Download client_secret.json and save to project root")
print("6. Update FOLDER_ID in this script with your Drive folder ID")
print()

# Check if client_secret.json exists
if not CLIENT_SECRET.exists():
    print(f"❌ ERROR: {CLIENT_SECRET} not found!")
    print()
    print("Please follow setup instructions above to create client_secret.json")
    exit(1)

# Check if folder ID is configured
if FOLDER_ID == "YOUR_GOOGLE_DRIVE_FOLDER_ID":
    print("❌ ERROR: FOLDER_ID not configured!")
    print()
    print("Please update FOLDER_ID in this script with your Google Drive folder ID")
    print("To get folder ID:")
    print("  1. Open the folder in Google Drive")
    print("  2. Copy the ID from URL: https://drive.google.com/drive/folders/FOLDER_ID")
    exit(1)

print("Starting download...")
print("-" * 80)
print(f"Folder ID: {FOLDER_ID}")
print(f"Output directory: {OUTPUT_DIR}")
print()

if not TOKEN_FILE.exists():
    print("First run - browser will open for OAuth consent")
    print("Please authorize the application to access Google Drive")
    print()

try:
    # Download files
    files = download_folder(
        folder_id=FOLDER_ID,
        out_dir=OUTPUT_DIR,
        client_secret_json=CLIENT_SECRET,
        token_json=TOKEN_FILE,
    )
    
    print()
    print("=" * 80)
    print("DOWNLOAD COMPLETED")
    print("=" * 80)
    print(f"Downloaded {len(files)} file(s):")
    print()
    
    for file_path in files:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ {file_path.name} ({size_mb:.2f} MB)")
    
    print()
    print(f"Files saved to: {OUTPUT_DIR.absolute()}")
    print(f"Token cached to: {TOKEN_FILE.absolute()}")
    print()
    print("Next runs will use cached token (no browser prompt)")
    
except Exception as e:
    print()
    print(f"❌ ERROR: {e}")
    print()
    print("Troubleshooting:")
    print("  - Verify folder ID is correct")
    print("  - Check that folder is shared with your Google account")
    print("  - Ensure Google Drive API is enabled in Cloud Console")
