"""
Script to upload Commercial-View exports to Google Drive

Run after processing to sync results with the export folder
"""

import os
import json
import glob
import argparse
from datetime import datetime
from typing import Dict, Optional, Tuple

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class DriveUploader:
    """Google Drive upload manager for Commercial-View exports"""

    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None

    def authenticate(self) -> bool:
        """Authenticate with Google Drive API"""
        if not GOOGLE_DRIVE_AVAILABLE:
            print("❌ Google Drive libraries not installed. Run:")
            print("   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            return False

        creds = None

        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    print(f"❌ Credentials file not found: {self.credentials_path}")
                    print("💡 Download from Google Cloud Console and place in project root")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('drive', 'v3', credentials=creds)
            return True
        except Exception as e:
            print(f"❌ Failed to build Drive service: {e}")
            return False

    def create_folder(self, name: str, parent_folder_id: str) -> Optional[str]:
        """Create a folder in Google Drive"""
        if not self.service:
            return None
            
        try:
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }

            folder = self.service.files().create(body=file_metadata, fields='id').execute()
            return folder.get('id')
        except Exception as e:
            print(f"❌ Failed to create folder '{name}': {e}")
            return None

    def upload_file(self, file_path: str, folder_id: str, filename: Optional[str] = None) -> bool:
        """Upload a single file to Google Drive"""
        if not self.service:
            return False
            
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        filename = filename or os.path.basename(file_path)

        try:
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }

            media = MediaFileUpload(file_path, resumable=True)

            request = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"📤 Uploading {filename}: {int(status.progress() * 100)}%")

            print(f"✅ Uploaded: {filename}")
            return True

        except Exception as e:
            print(f"❌ Failed to upload {filename}: {e}")
            return False


def load_config() -> Dict:
    """Load configuration from file or return defaults"""
    config_file = "drive_config.json"
    default_config = {
        "drive_folder_id": "1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8",
        "create_timestamped_folders": True,
        "upload_types": ["reports", "data", "manifests", "logs"]
    }

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"📋 Loaded config from {config_file}")
            return {**default_config, **config}
        except Exception as e:
            print(f"⚠️  Failed to load config: {e}, using defaults")

    return default_config


def find_latest_manifest(export_dir: str) -> Optional[Tuple[str, Dict]]:
    """Find and load the latest export manifest"""
    manifests = glob.glob(f"{export_dir}/export_manifest_*.json")
    if not manifests:
        print(f"❌ No export manifests found in {export_dir}")
        print("💡 Run the analysis pipeline first to generate exports")
        return None

    latest_manifest_path = max(manifests, key=os.path.getctime)

    try:
        with open(latest_manifest_path, 'r') as f:
            manifest = json.load(f)
        return latest_manifest_path, manifest
    except Exception as e:
        print(f"❌ Failed to load manifest {latest_manifest_path}: {e}")
        return None


def upload_exports_to_drive(
    export_dir: str = "./abaco_runtime/exports",
    config: Optional[Dict] = None,
    dry_run: bool = False
) -> bool:
    """Upload prepared export files to Google Drive folder"""

    config = config or load_config()

    # Find latest export manifest
    manifest_result = find_latest_manifest(export_dir)
    if not manifest_result:
        return False

    latest_manifest_path, manifest = manifest_result

    print(f"📤 Found export with {manifest.get('file_count', 0)} files")
    print(f"📋 Manifest: {latest_manifest_path}")
    print(f"🕒 Export timestamp: {manifest.get('export_timestamp', 'N/A')}")

    # List files and calculate total size
    total_size = 0
    files_to_upload = []

    for file_type, file_path in manifest.get('exported_files', {}).items():
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            total_size += file_size
            files_to_upload.append((file_type, file_path, file_size))
            print(f"  ✅ {file_type}: {file_path} ({file_size:,} bytes)")
        else:
            print(f"  ❌ {file_type}: {file_path} (FILE NOT FOUND)")

    print(f"\n📊 Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")

    if dry_run:
        print("\n🔍 DRY RUN - No files will be uploaded")
        print(f"🔗 Target folder: https://drive.google.com/drive/folders/{config['drive_folder_id']}")
        return True

    if not files_to_upload:
        print("❌ No valid files found to upload")
        return False

    # Initialize Drive uploader
    uploader = DriveUploader()
    if not uploader.authenticate():
        return False

    # Determine target folder
    target_folder_id = config['drive_folder_id']

    # Create timestamped subfolder if configured
    if config.get('create_timestamped_folders', False):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_timestamp = manifest.get('export_timestamp', timestamp)
        folder_name = f"export_{export_timestamp}"

        print(f"📁 Creating timestamped folder: {folder_name}")
        subfolder_id = uploader.create_folder(folder_name, target_folder_id)
        if subfolder_id:
            target_folder_id = subfolder_id
        else:
            print("⚠️  Failed to create subfolder, uploading to root folder")

    # Upload files
    success_count = 0
    for file_type, file_path, file_size in files_to_upload:
        if file_type in config.get('upload_types', []):
            if uploader.upload_file(file_path, target_folder_id):
                success_count += 1
        else:
            print(f"⏭️  Skipping {file_type} (not in upload_types)")

    print(f"\n🎉 Upload complete: {success_count}/{len(files_to_upload)} files uploaded")
    print(f"🔗 View files: https://drive.google.com/drive/folders/{target_folder_id}")

    return success_count > 0


def main():
    """Main entry point with command-line interface"""
    parser = argparse.ArgumentParser(description="Upload Commercial-View exports to Google Drive")

    parser.add_argument(
        "--export-dir",
        default="./abaco_runtime/exports",
        help="Directory containing export manifests (default: ./abaco_runtime/exports)"
    )

    parser.add_argument(
        "--config",
        help="Path to custom configuration file"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without actually uploading"
    )

    parser.add_argument(
        "--folder-id",
        help="Google Drive folder ID (overrides config)"
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config()
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            custom_config = json.load(f)
        config.update(custom_config)

    if args.folder_id:
        config['drive_folder_id'] = args.folder_id

    print("🚀 Commercial-View Google Drive Upload")
    print(f"📂 Export directory: {args.export_dir}")
    print(f"🎯 Target folder ID: {config['drive_folder_id']}")

    success = upload_exports_to_drive(
        export_dir=args.export_dir,
        config=config,
        dry_run=args.dry_run
    )

    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
