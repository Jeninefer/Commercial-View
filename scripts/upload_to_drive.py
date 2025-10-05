"""
Script to upload Commercial-View exports to Google Drive
Run after processing to sync results with the export folder
"""

import os
import json
import glob

def upload_exports_to_drive():
    """Upload prepared export files to Google Drive folder"""
    export_dir = "./abaco_runtime/exports"
    drive_folder_id = "1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8"
    
    # Find latest export manifest
    manifests = glob.glob(f"{export_dir}/export_manifest_*.json")
    if not manifests:
        print("No export manifests found. Run analysis first.")
        return
    
    latest_manifest = max(manifests, key=os.path.getctime)
    
    with open(latest_manifest, 'r') as f:
        manifest = json.load(f)
    
    print(f"📤 Ready to upload {manifest['file_count']} files to Google Drive")
    print(f"🔗 Target folder: https://drive.google.com/drive/folders/{drive_folder_id}")
    print(f"📋 Manifest: {latest_manifest}")
    print(f"🕒 Export timestamp: {manifest.get('export_timestamp', 'N/A')}")
    
    # List files ready for upload
    total_size = 0
    for file_type, file_path in manifest['exported_files'].items():
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            total_size += file_size
            print(f"  - {file_type}: {file_path} ({file_size:,} bytes)")
        else:
            print(f"  - {file_type}: {file_path} (FILE NOT FOUND)")
    
    print(f"\n📊 Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    print("\n💡 To upload files, use Google Drive API or manually copy files to:")
    print(f"   https://drive.google.com/drive/folders/{drive_folder_id}")

if __name__ == "__main__":
    upload_exports_to_drive()
