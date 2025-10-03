"""
Example: Google Drive integration

Demonstrates how to use GoogleDriveIngestor for OAuth-based file access.

Prerequisites:
1. Create credentials.json from Google Cloud Console
2. Set GOOGLE_CREDENTIALS_PATH in .env
3. Run script and complete OAuth flow in browser
"""

import os
from pathlib import Path

# Check if Google Drive dependencies are available
try:
    from abaco_core import GoogleDriveIngestor
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False
    print("Google Drive dependencies not installed.")
    print("Install with: pip install google-auth google-auth-oauthlib google-api-python-client")


def main():
    if not GDRIVE_AVAILABLE:
        print("\nSkipping example - install Google API libraries first")
        return
    
    print("=== Google Drive Integration Example ===\n")
    
    # Check for credentials
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    if not Path(creds_path).exists():
        print(f"ERROR: Credentials file not found: {creds_path}")
        print("\nTo set up Google Drive integration:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Drive API")
        print("4. Create OAuth 2.0 credentials (Desktop application)")
        print("5. Download as 'credentials.json'")
        print("6. Set GOOGLE_CREDENTIALS_PATH in .env")
        return
    
    try:
        # Initialize ingestor (will prompt for OAuth on first use)
        print("Initializing Google Drive ingestor...")
        print("If this is your first time, a browser window will open for OAuth authentication.")
        ingestor = GoogleDriveIngestor()
        print("✓ Authentication successful\n")
        
        # Example 1: List files
        print("=== Example 1: List Files ===")
        print("Listing recent files...")
        files = ingestor.list_files(max_results=10)
        
        if files:
            print(f"\nFound {len(files)} files:")
            for file in files[:5]:  # Show first 5
                print(f"  - {file['name']} ({file['mimeType']})")
                print(f"    ID: {file['id']}")
                print(f"    Modified: {file['modifiedTime']}")
        else:
            print("No files found")
        
        # Example 2: Filter files
        print("\n=== Example 2: Filter Files ===")
        print("Searching for CSV files...")
        csv_files = ingestor.list_files(
            mime_type="text/csv",
            max_results=5
        )
        
        if csv_files:
            print(f"\nFound {len(csv_files)} CSV files:")
            for file in csv_files:
                print(f"  - {file['name']}")
        else:
            print("No CSV files found")
        
        # Example 3: Download a file (commented out - requires file ID)
        print("\n=== Example 3: Download File ===")
        print("To download a file:")
        print("  content = ingestor.download_file(file_id='YOUR_FILE_ID')")
        print("  # Or save directly:")
        print("  ingestor.download_file(")
        print("      file_id='YOUR_FILE_ID',")
        print("      output_path=Path('./data/portfolio.csv')")
        print("  )")
        
        # Example 4: Download folder (commented out - requires folder ID)
        print("\n=== Example 4: Download Folder ===")
        print("To download all files from a folder:")
        print("  paths = ingestor.download_folder(")
        print("      folder_id='YOUR_FOLDER_ID',")
        print("      output_dir=Path('./data'),")
        print("      mime_type='text/csv'  # Optional filter")
        print("  )")
        
        print("\n✓ All examples completed successfully")
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nTroubleshooting:")
        print("- Ensure credentials.json is valid")
        print("- Check internet connection")
        print("- Verify Google Drive API is enabled")


if __name__ == "__main__":
    main()
