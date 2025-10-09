"""
Data Ingestion Module for Commercial-View Analytics Pipeline

Handles data loading from multiple sources:
- Local CSV files
- Google Sheets
- Google Drive
- Excel files
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import gspread
import io


class DataIngestionManager:
    """Manages data ingestion from multiple sources"""
    
    def __init__(self, config: Dict):
        """
        Initialize data ingestion manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.credentials = None
        self.gspread_client = None
        self.drive_service = None
        self.sheets_service = None
        
        self._initialize_google_apis()
    
    def _initialize_google_apis(self):
        """Initialize Google API clients"""
        credentials_path = self.config.get('credentials_path')
        
        if not credentials_path or not Path(credentials_path).exists():
            print("⚠️  Google credentials not found. Using local data only.")
            return
        
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=scopes
            )
            
            self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            self.gspread_client = gspread.authorize(self.credentials)
            
            print("✅ Google API clients initialized")
            
        except Exception as e:
            print(f"⚠️  Failed to initialize Google APIs: {e}")
    
    def load_csv_file(self, filename: str, data_dir: Optional[Path] = None) -> pd.DataFrame:
        """
        Load data from CSV file
        
        Args:
            filename: Name of CSV file
            data_dir: Directory containing CSV files
            
        Returns:
            DataFrame with loaded data
        """
        if data_dir is None:
            data_dir = self.config.get('data_dir')
        
        filepath = Path(data_dir) / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            print(f"✅ Loaded {len(df):,} rows from {filename}")
            return df
        except Exception as e:
            raise Exception(f"Failed to load CSV {filename}: {e}")
    
    def load_google_sheet(self, sheet_id: str, tab_name: str) -> pd.DataFrame:
        """
        Load data from Google Sheet
        
        Args:
            sheet_id: Google Sheet ID
            tab_name: Name of tab/worksheet
            
        Returns:
            DataFrame with loaded data
        """
        if self.gspread_client is None:
            raise Exception("Google Sheets client not initialized")
        
        try:
            sheet = self.gspread_client.open_by_key(sheet_id)
            worksheet = sheet.worksheet(tab_name)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            print(f"✅ Loaded {len(df):,} rows from Google Sheet tab '{tab_name}'")
            return df
        except Exception as e:
            raise Exception(f"Failed to load Google Sheet tab '{tab_name}': {e}")
    
    def load_excel_file(self, filename: str, sheet_name: str = 0) -> pd.DataFrame:
        """
        Load data from Excel file
        
        Args:
            filename: Name of Excel file
            sheet_name: Name or index of sheet
            
        Returns:
            DataFrame with loaded data
        """
        filepath = Path(self.config.get('data_dir')) / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Excel file not found: {filepath}")
        
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            print(f"✅ Loaded {len(df):,} rows from Excel: {filename} (sheet: {sheet_name})")
            return df
        except Exception as e:
            raise Exception(f"Failed to load Excel {filename}: {e}")
    
    def download_from_drive(self, file_id: str, destination: Path) -> Path:
        """
        Download file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            destination: Local destination path
            
        Returns:
            Path to downloaded file
        """
        if self.drive_service is None:
            raise Exception("Google Drive service not initialized")
        
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"   Download {int(status.progress() * 100)}%")
            
            # Write to file
            destination.parent.mkdir(parents=True, exist_ok=True)
            with open(destination, 'wb') as f:
                f.write(fh.getvalue())
            
            print(f"✅ Downloaded file to: {destination}")
            return destination
            
        except Exception as e:
            raise Exception(f"Failed to download from Drive: {e}")
    
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all required datasets
        
        Returns:
            Dictionary of DataFrames
        """
        data = {}
        data_sources = self.config.get('data_sources', {})
        
        # Load CSV files
        csv_files = {
            'loan_data': data_sources.get('loan_data', 'Abaco - Loan Tape_Loan Data_Table.csv'),
            'customer_data': data_sources.get('customer_data', 'Abaco - Loan Tape_Customer Data_Table.csv'),
            'collateral': data_sources.get('collateral_data', 'Abaco - Loan Tape_Collateral_Table.csv'),
            'payment_history': data_sources.get('payment_history', 'Abaco - Loan Tape_Historic Real Payment_Table.csv'),
            'payment_schedule': data_sources.get('payment_schedule', 'Abaco - Loan Tape_Payment Schedule_Table.csv'),
        }
        
        for key, filename in csv_files.items():
            try:
                data[key] = self.load_csv_file(filename)
            except FileNotFoundError:
                print(f"⚠️  {filename} not found, skipping...")
                data[key] = pd.DataFrame()
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
                data[key] = pd.DataFrame()
        
        # Load financial statements (Excel)
        try:
            financials_file = data_sources.get('financials', 'financials-abaco-consolidated-financials.xlsx')
            data['financials_pl'] = self.load_excel_file(financials_file, 'Profit and Loss')
            data['financials_bs'] = self.load_excel_file(financials_file, 'Balance Sheet')
        except Exception as e:
            print(f"⚠️  Could not load financial statements: {e}")
        
        print(f"\n📊 Data Loading Summary:")
        print(f"   Total datasets loaded: {len([d for d in data.values() if not d.empty])}/{len(data)}")
        
        return data
    
    def validate_data_quality(self, df: pd.DataFrame, dataset_name: str, 
                             max_missing_pct: float = 0.15) -> bool:
        """
        Validate data quality
        
        Args:
            df: DataFrame to validate
            dataset_name: Name of dataset
            max_missing_pct: Maximum allowed missing data percentage
            
        Returns:
            True if validation passes
        """
        if df.empty:
            print(f"❌ {dataset_name}: Dataset is empty")
            return False
        
        # Check missing data
        missing_pct = df.isnull().sum().sum() / (len(df) * len(df.columns))
        
        if missing_pct > max_missing_pct:
            print(f"⚠️  {dataset_name}: High missing data ({missing_pct:.1%} > {max_missing_pct:.1%})")
            return False
        
        print(f"✅ {dataset_name}: Quality check passed (missing: {missing_pct:.1%})")
        return True


# Convenience functions for backward compatibility
def load_loan_data(data_dir: str = None) -> pd.DataFrame:
    """Load loan data (backward compatible)"""
    from src.utils.config_loader import load_config
    config = load_config().to_dict()
    if data_dir:
        config['data_dir'] = Path(data_dir)
    
    ingestion = DataIngestionManager(config)
    return ingestion.load_csv_file(config['data_sources']['loan_data'])


def load_customer_data(data_dir: str = None) -> pd.DataFrame:
    """Load customer data (backward compatible)"""
    from src.utils.config_loader import load_config
    config = load_config().to_dict()
    if data_dir:
        config['data_dir'] = Path(data_dir)
    
    ingestion = DataIngestionManager(config)
    return ingestion.load_csv_file(config['data_sources']['customer_data'])
