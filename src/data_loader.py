"""
Production data loader for Commercial-View
Loads real CSV data from Google Drive folder
"""

import os
import pandas as pd
import gdown
from pathlib import Path
from typing import Dict, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProductionDataLoader:
    """Production data loader for real Commercial-View CSV files"""
    
    def __init__(self):
        self.drive_folder_url = "https://drive.google.com/drive/folders/1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8"
        self.local_data_dir = Path("data")
        self.local_data_dir.mkdir(exist_ok=True)
        
        # Expected real CSV files (no demo data)
        self.expected_files = {
            "loan_data": "loan_data.csv",
            "payment_schedule": "payment_schedule.csv", 
            "historic_payments": "historic_real_payment.csv",
            "customer_data": "customer_data.csv",
            "collateral_data": "collateral_data.csv"
        }
        
    def download_production_data(self) -> Dict[str, bool]:
        """Download real CSV files from Google Drive"""
        results = {}
        
        logger.info(f"Downloading production data from: {self.drive_folder_url}")
        
        try:
            # Download entire folder
            gdown.download_folder(
                self.drive_folder_url,
                output=str(self.local_data_dir),
                quiet=False,
                use_cookies=False
            )
            
            # Verify downloaded files
            for file_key, filename in self.expected_files.items():
                file_path = self.local_data_dir / filename
                results[file_key] = file_path.exists()
                
                if results[file_key]:
                    logger.info(f"✅ Downloaded: {filename}")
                else:
                    logger.warning(f"❌ Missing: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to download production data: {e}")
            for file_key in self.expected_files:
                results[file_key] = False
        
        return results
    
    def load_production_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load all production CSV files into DataFrames"""
        datasets = {}
        
        for file_key, filename in self.expected_files.items():
            file_path = self.local_data_dir / filename
            
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    datasets[file_key] = df
                    logger.info(f"✅ Loaded {filename}: {len(df)} rows, {len(df.columns)} columns")
                except Exception as e:
                    logger.error(f"❌ Failed to load {filename}: {e}")
            else:
                logger.warning(f"⚠️  File not found: {filename}")
        
        return datasets
    
    def validate_production_data(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Validate production data quality"""
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_datasets": len(datasets),
            "validation_passed": True,
            "issues": []
        }
        
        for name, df in datasets.items():
            if df.empty:
                validation_results["issues"].append(f"{name}: Dataset is empty")
                validation_results["validation_passed"] = False
            
            # Check for required columns based on dataset type
            required_columns = self.get_required_columns(name)
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                validation_results["issues"].append(
                    f"{name}: Missing required columns: {missing_columns}"
                )
                validation_results["validation_passed"] = False
        
        return validation_results
    
    def get_required_columns(self, dataset_name: str) -> List[str]:
        """Get required columns for each dataset type"""
        column_requirements = {
            "loan_data": ["loan_id", "customer_id", "principal_amount", "interest_rate"],
            "payment_schedule": ["payment_id", "loan_id", "due_date", "amount"],
            "historic_payments": ["loan_id", "payment_date", "amount_paid", "days_past_due"],
            "customer_data": ["customer_id", "name", "credit_score"],
            "collateral_data": ["collateral_id", "loan_id", "type", "value"]
        }
        
        return column_requirements.get(dataset_name, [])

# Remove any demo/example data functions
class DataLoader:
    """Main data loader class for production use"""
    
    def __init__(self):
        self.production_loader = ProductionDataLoader()
    
    def load_all_data(self, force_download: bool = False) -> Dict[str, pd.DataFrame]:
        """Load all production data with optional force download"""
        
        # Check if we need to download fresh data
        if force_download or not self.has_local_data():
            logger.info("Downloading fresh production data...")
            download_results = self.production_loader.download_production_data()
            
            if not any(download_results.values()):
                logger.error("No production data could be downloaded")
                return {}
        
        # Load datasets
        datasets = self.production_loader.load_production_datasets()
        
        # Validate data quality
        validation = self.production_loader.validate_production_data(datasets)
        
        if not validation["validation_passed"]:
            logger.warning("Data validation issues found:")
            for issue in validation["issues"]:
                logger.warning(f"  - {issue}")
        
        return datasets
    
    def has_local_data(self) -> bool:
        """Check if we have local data files"""
        return any(
            (self.production_loader.local_data_dir / filename).exists()
            for filename in self.production_loader.expected_files.values()
        )
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of available production data"""
        datasets = self.load_all_data()
        
        summary = {
            "total_datasets": len(datasets),
            "datasets": {}
        }
        
        for name, df in datasets.items():
            summary["datasets"][name] = {
                "rows": len(df),
                "columns": len(df.columns),
                "memory_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
                "last_modified": datetime.now().isoformat()
            }
        
        return summary

# Remove any sample data generators or demo functions
def get_production_data() -> Dict[str, pd.DataFrame]:
    """Get production data - no demo/example data"""
    loader = DataLoader()
    return loader.load_all_data()

def refresh_production_data() -> bool:
    """Refresh production data from Google Drive"""
    loader = DataLoader()
    datasets = loader.load_all_data(force_download=True)
    return len(datasets) > 0
