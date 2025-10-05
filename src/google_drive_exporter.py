"""
Google Drive export integration for Commercial-View results
Automatically uploads analysis results to specified Google Drive folder
"""

import json
import pandas as pd
from typing import Dict, Any
from datetime import datetime

class GoogleDriveExporter:
    """Export Commercial-View results to Google Drive folder"""
    
    def __init__(self, drive_folder_id: str = "1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8"):
        self.drive_folder_id = drive_folder_id
        self.export_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def prepare_export_files(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Prepare analysis results for Google Drive export"""
        export_files: Dict[str, str] = {}
        
        # Export comprehensive analytics as JSON
        json_filename = f"commercial_view_analytics_{self.export_timestamp}.json"
        json_path = f"./abaco_runtime/exports/{json_filename}"
        
        with open(json_path, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        export_files['analytics_json'] = json_path
        
        # Export KPI summary as CSV
        if 'portfolio_summary' in analysis_results:
            csv_filename = f"kpi_summary_{self.export_timestamp}.csv"
            csv_path = f"./abaco_runtime/exports/{csv_filename}"
            
            kpi_data = pd.DataFrame([analysis_results['portfolio_summary']])
            kpi_data.to_csv(csv_path, index=False)
            export_files['kpi_csv'] = csv_path
        
        # Export customer classifications
        if 'customer_type_distribution' in analysis_results:
            customer_filename = f"customer_classifications_{self.export_timestamp}.json"
            customer_path = f"./abaco_runtime/exports/{customer_filename}"
            
            with open(customer_path, 'w') as f:
                json.dump(analysis_results['customer_type_distribution'], f, indent=2)
            export_files['customer_json'] = customer_path
        
        return export_files
    
    def generate_export_manifest(self, export_files: Dict[str, str]) -> str:
        """Generate manifest file for Google Drive exports"""
        manifest: Dict[str, Any] = {
            "export_timestamp": self.export_timestamp,
            "drive_folder_id": self.drive_folder_id,
            "drive_folder_url": f"https://drive.google.com/drive/folders/{self.drive_folder_id}",
            "exported_files": export_files,
            "file_count": len(export_files),
            "export_status": "ready_for_upload"
        }
        
        manifest_path = f"./abaco_runtime/exports/export_manifest_{self.export_timestamp}.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest_path
