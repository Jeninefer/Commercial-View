"""
Script to upload Commercial-View exports to Google Drive

Run after processing to sync results with the export folder

Prerequisites:
    pip install google-auth-oauthlib google-api-python-client google-auth-httplib2
"""

import os
import json
import glob
import argparse
import sys
import time
from datetime import datetime
from typing import Dict, Optional, Tuple, Any, List
from pathlib import Path

# Check for required Google API libraries with better error handling
GOOGLE_DRIVE_AVAILABLE = False
MISSING_IMPORT_ERROR = ""

try:
    # Import Google API client libraries
    from googleapiclient.discovery import build  # type: ignore
    from googleapiclient.http import MediaFileUpload  # type: ignore
    from google.auth.transport.requests import Request  # type: ignore
    from google.oauth2.credentials import Credentials  # type: ignore
    from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError as e:
    MISSING_IMPORT_ERROR = str(e)
    # Create mock classes to prevent further import errors
    class MockCredentials:
        def __init__(self): pass
        @staticmethod
        def from_authorized_user_file(*args): return None
        @property
        def valid(self): return False
        @property
        def expired(self): return True
        @property
        def refresh_token(self): return None
        def refresh(self, *args): pass
        def to_json(self): return "{}"
    
    class MockInstalledAppFlow:
        @staticmethod
        def from_client_secrets_file(*args): return None
        def run_local_server(self, *args): return None
    
    # Use mock classes - assign the class itself, not an instance
    Credentials = MockCredentials
    InstalledAppFlow = MockInstalledAppFlow
    build = lambda *args, **kwargs: None  # type: ignore
    MediaFileUpload = lambda *args, **kwargs: None  # type: ignore
    Request = lambda: None  # type: ignore

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def install_google_dependencies() -> bool:
    """Install Google API dependencies automatically"""
    print("🔄 Attempting to install Google API dependencies...")
    
    packages = [
        "google-auth-oauthlib",
        "google-api-python-client", 
        "google-auth-httplib2",
        "google-auth"
    ]
    
    try:
        import subprocess
        for package in packages:
            print(f"   Installing {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"   ❌ Failed to install {package}: {result.stderr}")
                return False
            else:
                print(f"   ✅ Installed {package}")
        
        print("\n✅ All Google API dependencies installed successfully!")
        print("🔄 Please restart the script to use the new dependencies.")
        return True
        
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False


def check_dependencies() -> bool:
    """Check if all required dependencies are installed"""
    if not GOOGLE_DRIVE_AVAILABLE:
        print("❌ Google Drive API libraries are not installed!")
        print(f"   Import error: {MISSING_IMPORT_ERROR}")
        print("\n🔧 To fix this, you have two options:")
        print("\n1. Install manually:")
        print("   pip install google-auth-oauthlib google-api-python-client google-auth-httplib2")
        print("\n2. Let this script install for you (press 'y' to continue):")
        
        try:
            response = input("   Install dependencies automatically? (y/n): ").lower().strip()
            if response == 'y':
                return install_google_dependencies()
        except KeyboardInterrupt:
            print("\n❌ Installation cancelled by user")
        
        print("\n💡 If you're using a virtual environment, make sure it's activated first:")
        print("   source .venv/bin/activate  # On macOS/Linux")
        print("   .venv\\Scripts\\activate     # On Windows")
        return False
    return True


class DriveUploader:
    """Google Drive upload manager for Commercial-View exports"""

    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.upload_history: List[Dict[str, Any]] = []

    def authenticate(self) -> bool:
        """Authenticate with Google Drive API"""
        if not check_dependencies():
            return False

        creds = self._load_or_refresh_credentials()
        if not creds:
            return False

        return self._build_drive_service(creds)

    def _print_installation_instructions(self) -> None:
        """Print Google Drive library installation instructions"""
        check_dependencies()

    def _load_or_refresh_credentials(self) -> Optional[Credentials]:
        """Load existing credentials or get new ones"""
        creds = None

        # Load existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            creds = self._handle_invalid_credentials(creds)

        return creds

    def _handle_invalid_credentials(self, creds: Optional[Credentials]) -> Optional[Credentials]:
        """Handle invalid or expired credentials"""
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = self._get_new_credentials()
            if not creds:
                return None

        # Save credentials for next run
        with open(self.token_path, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())

        return creds

    def _get_new_credentials(self) -> Optional[Credentials]:
        """Get new credentials from OAuth flow"""
        if not os.path.exists(self.credentials_path):
            print(f"❌ Credentials file not found: {self.credentials_path}")
            print("💡 Download from Google Cloud Console and place in project root")
            return None

        flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
        return flow.run_local_server(port=0)

    def _build_drive_service(self, creds: Credentials) -> bool:
        """Build the Google Drive service"""
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

    def upload_file_with_retry(self, file_path: str, folder_id: str, filename: Optional[str] = None, max_retries: int = 3) -> bool:
        """Upload a single file to Google Drive with retry logic"""
        if not self.service:
            return False
            
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        filename = filename or os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        for attempt in range(max_retries):
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
                last_progress = 0
                start_time = time.time()
                
                while response is None:
                    try:
                        status, response = request.next_chunk()
                        if status:
                            progress = int(status.progress() * 100)
                            if progress - last_progress >= 10:  # Update every 10%
                                elapsed = time.time() - start_time
                                speed = (file_size * status.progress()) / (1024 * 1024 * elapsed) if elapsed > 0 else 0
                                print(f"📤 Uploading {filename}: {progress}% ({speed:.1f} MB/s)")
                                last_progress = progress
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"⚠️  Upload interrupted, retrying... (attempt {attempt + 1}/{max_retries})")
                            time.sleep(2 ** attempt)  # Exponential backoff
                            break
                        else:
                            raise e

                if response:
                    upload_time = time.time() - start_time
                    avg_speed = (file_size / (1024 * 1024)) / upload_time if upload_time > 0 else 0
                    
                    # Record upload history
                    self.upload_history.append({
                        'filename': filename,
                        'size_mb': file_size / (1024 * 1024),
                        'upload_time_seconds': upload_time,
                        'avg_speed_mbps': avg_speed,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    print(f"✅ Uploaded: {filename} ({avg_speed:.1f} MB/s avg)")
                    return True

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"❌ Upload failed (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"❌ Failed to upload {filename} after {max_retries} attempts: {e}")
                    return False

        return False

    def upload_file(self, file_path: str, folder_id: str, filename: Optional[str] = None) -> bool:
        """Upload a single file to Google Drive (backward compatibility)"""
        return self.upload_file_with_retry(file_path, folder_id, filename)

    def get_upload_statistics(self) -> Dict[str, Any]:
        """Get upload statistics"""
        if not self.upload_history:
            return {}
        
        total_files = len(self.upload_history)
        total_size_mb = sum(upload['size_mb'] for upload in self.upload_history)
        total_time = sum(upload['upload_time_seconds'] for upload in self.upload_history)
        avg_speed = sum(upload['avg_speed_mbps'] for upload in self.upload_history) / total_files
        
        return {
            'total_files': total_files,
            'total_size_mb': total_size_mb,
            'total_time_seconds': total_time,
            'average_speed_mbps': avg_speed,
            'files_per_minute': (total_files / (total_time / 60)) if total_time > 0 else 0
        }

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


def process_upload_files(manifest: Dict) -> Tuple[int, list]:
    """Process manifest files and calculate upload metrics"""
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

    return total_size, files_to_upload


def create_upload_folder(uploader: DriveUploader, config: Dict, manifest: Dict) -> str:
    """Create timestamped folder if configured"""
    target_folder_id = config['drive_folder_id']

    if config.get('create_timestamped_folders', False):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_timestamp = manifest.get('export_timestamp', timestamp)
        folder_name = f"export_{export_timestamp}"

        print(f"📁 Creating timestamped folder: {folder_name}")
        subfolder_id = uploader.create_folder(folder_name, target_folder_id)
        if subfolder_id:
            return subfolder_id
        else:
            print("⚠️  Failed to create subfolder, uploading to root folder")

    return target_folder_id


def create_upload_summary(uploader: DriveUploader, config: Dict, success_count: int, total_files: int) -> None:
    """Create and save upload summary"""
    stats = uploader.get_upload_statistics()
    
    summary = {
        'upload_session': {
            'timestamp': datetime.now().isoformat(),
            'success_count': success_count,
            'total_files': total_files,
            'success_rate': (success_count / total_files * 100) if total_files > 0 else 0,
            'target_folder_id': config['drive_folder_id']
        },
        'performance': stats,
        'upload_history': uploader.upload_history
    }
    
    # Save summary to file
    summary_file = f"upload_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"📄 Upload summary saved to: {summary_file}")
    except Exception as e:
        print(f"⚠️  Could not save upload summary: {e}")
    
    # Print summary
    if stats:
        print(f"\n📊 Upload Statistics:")
        print(f"   Files uploaded: {stats['total_files']}")
        print(f"   Total size: {stats['total_size_mb']:.2f} MB")
        print(f"   Total time: {stats['total_time_seconds']:.1f} seconds")
        print(f"   Average speed: {stats['average_speed_mbps']:.2f} MB/s")
        print(f"   Upload rate: {stats['files_per_minute']:.1f} files/minute")

def validate_export_directory(export_dir: str) -> bool:
    """Validate that the export directory exists and contains expected files"""
    if not os.path.exists(export_dir):
        print(f"❌ Export directory does not exist: {export_dir}")
        return False
    
    # Check for manifest files
    manifests = glob.glob(f"{export_dir}/export_manifest_*.json")
    if not manifests:
        print(f"❌ No export manifests found in {export_dir}")
        print("💡 Expected files: export_manifest_YYYYMMDD_HHMMSS.json")
        return False
    
    print(f"✅ Found {len(manifests)} export manifest(s) in {export_dir}")
    return True

def perform_file_uploads(uploader: DriveUploader, files_to_upload: list, target_folder_id: str, config: Dict) -> int:
    """Perform the actual file uploads with enhanced progress tracking"""
    success_count = 0
    total_files = len([f for f in files_to_upload if f[0] in config.get('upload_types', [])])
    current_file = 0
    
    print(f"\n🚀 Starting upload of {total_files} files...")
    
    for file_type, file_path, file_size in files_to_upload:
        if file_type in config.get('upload_types', []):
            current_file += 1
            print(f"\n[{current_file}/{total_files}] Processing {file_type}...")
            
            if uploader.upload_file_with_retry(file_path, target_folder_id):
                success_count += 1
            else:
                print(f"⚠️  Continuing with remaining files...")
        else:
            print(f"⏭️  Skipping {file_type} (not in upload_types)")
    
    return success_count

def upload_exports_to_drive(
    export_dir: str = "./abaco_runtime/exports",
    config: Optional[Dict] = None,
    dry_run: bool = False
) -> bool:
    """Upload prepared export files to Google Drive folder"""

    if config is None:
        config = load_config()

    # Validate export directory
    if not validate_export_directory(export_dir):
        return False

    # Find latest export manifest
    manifest_result = find_latest_manifest(export_dir)
    if not manifest_result:
        return False

    latest_manifest_path, manifest = manifest_result

    print(f"📤 Found export with {manifest.get('file_count', 0)} files")
    print(f"📋 Manifest: {latest_manifest_path}")
    print(f"🕒 Export timestamp: {manifest.get('export_timestamp', 'N/A')}")

    # Process files and calculate metrics
    total_size, files_to_upload = process_upload_files(manifest)
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

    # Create upload folder
    target_folder_id = create_upload_folder(uploader, config, manifest)

    # Perform uploads
    success_count = perform_file_uploads(uploader, files_to_upload, target_folder_id, config)

    # Create upload summary
    create_upload_summary(uploader, config, success_count, len(files_to_upload))

    print(f"\n🎉 Upload complete: {success_count}/{len(files_to_upload)} files uploaded")
    print(f"🔗 View files: https://drive.google.com/drive/folders/{target_folder_id}")

    return success_count > 0

def main():
    """Main entry point with command-line interface"""
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Cannot proceed without required Google API libraries")
        return 1

    parser = argparse.ArgumentParser(
        description="Upload Commercial-View exports to Google Drive",
        epilog="""
Prerequisites:
    pip install google-auth-oauthlib google-api-python-client google-auth-httplib2

Examples:
    python upload_to_drive.py --dry-run
    python upload_to_drive.py --export-dir ./exports --folder-id YOUR_FOLDER_ID
    python upload_to_drive.py --validate-only
        """
    )

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
        "--validate-only",
        action="store_true",
        help="Only validate export directory and manifests"
    )

    parser.add_argument(
        "--folder-id",
        help="Google Drive folder ID (overrides config)"
    )

    args = parser.parse_args()

    # Validate export directory first
    if not validate_export_directory(args.export_dir):
        return 1
    
    if args.validate_only:
        print("✅ Export directory validation passed")
        return 0

    # Load configuration
    config = load_config()
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
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
    sys.exit(main())
