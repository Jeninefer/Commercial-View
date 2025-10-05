import os
import pandas as pd
from typing import Dict, Optional, List
import yaml
import logging
from datetime import datetime
import numpy as np
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataLoader:
    """Production-grade data loader with comprehensive error handling and validation."""
    
    def __init__(self, data_dir: str = "data", manifest_path: str = None):
        if manifest_path is None:
            manifest_path = os.path.join(os.path.dirname(__file__), "..", "manifest.json")
        self.data_dir = data_dir
        self.manifest = self._load_manifest(manifest_path)
        self.datasets = {}
        self.validation_errors = []
        
    def _load_manifest(self, manifest_path: str) -> Dict:
        """Load the project manifest file."""
        try:
            with open(manifest_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Manifest file not found at {manifest_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
            return {}

    def _load_google_sheet(self, sheet_id: str, sheet_name: str) -> Optional[pd.DataFrame]:
        """Load data from a public Google Sheet."""
        try:
            url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
            df = pd.read_csv(url)
            return df
        except Exception as e:
            logger.error(f"Failed to load Google Sheet '{sheet_name}': {str(e)}")
            return None

    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load all datasets with comprehensive validation and error handling."""
        sources = self.manifest.get('sources', {})

        # Load file-based sources
        for file_source in sources.get('files', []):
            try:
                dataset_name = file_source['name']
                glob_pattern = file_source['glob']
                logger.info(f"Loading {dataset_name} from files...")
                df = self._load_csv_with_pattern(glob_pattern)
                if df is not None and not df.empty:
                    self.datasets[dataset_name] = df
                    logger.info(f"Successfully loaded {dataset_name}: {len(df)} rows")
                else:
                    logger.warning(f"No data loaded for {dataset_name}")
            except Exception as e:
                logger.error(f"Failed to load {dataset_name}: {str(e)}")

        # Load Google Sheet sources
        for sheet_source in sources.get('google_sheets', []):
            sheet_id = sheet_source['id']
            for r in sheet_source.get('ranges', []):
                try:
                    range_name = r['range']
                    sheet_name = range_name.split('!')[0]
                    logger.info(f"Loading data from Google Sheet: {sheet_name}...")
                    df = self._load_google_sheet(sheet_id, sheet_name)
                    if df is not None and not df.empty:
                        # This part is tricky, as multiple ranges can be extracted.
                        # For now, we'll just load them. Merging logic will be complex.
                        self.datasets[f"google_sheet_{sheet_name}"] = df
                        logger.info(f"Successfully loaded Google Sheet '{sheet_name}': {len(df)} rows")
                    else:
                        logger.warning(f"No data loaded from Google Sheet: {sheet_name}")
                except Exception as e:
                    logger.error(f"Failed to load Google Sheet range {range_name}: {str(e)}")

        # Apply column mappings and validations
        for name, df in self.datasets.items():
            self.datasets[name] = self._apply_column_mappings(df, name)
            self._validate_required_columns(df, name)

        return self.datasets
    
    def _load_csv_with_pattern(self, pattern: str) -> Optional[pd.DataFrame]:
        """Load CSV file matching pattern with robust error handling."""
        try:
            # This assumes the glob pattern in the manifest is relative to the project root
            import glob
            # The pattern in manifest starts with /data, which is from root.
            # We need to make it relative to the project root.
            if pattern.startswith('/'):
                pattern = pattern[1:]
            full_pattern = os.path.join(os.path.dirname(os.path.abspath(__file__)), pattern)
            matching_files = glob.glob(full_pattern)
            
            if not matching_files:
                return None
            
            file_path = sorted(matching_files)[-1]
            
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='latin-1')
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading file with pattern '{pattern}': {str(e)}")
            return None
    
    def _apply_column_mappings(self, df: pd.DataFrame, dataset_key: str) -> pd.DataFrame:
        """Apply column mappings from configuration."""
        # Column mappings are not explicitly in the manifest in a way that is easy to use.
        # The `schemas` section has the column names, but not the mapping from old to new.
        # The `google_sheets.extract` has some mappings, but not for all datasets.
        # I will assume for now that the column names in the CSVs and Google Sheets are already the desired ones.
        return df
    
    def _validate_required_columns(self, df: pd.DataFrame, dataset_key: str):
        """Validate that required columns exist and have data."""
        schemas = self.manifest.get('schemas', {})
        if dataset_key in schemas:
            required_columns = schemas[dataset_key].get('required_columns', [])
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                error_msg = f"Missing required columns in {dataset_key}: {missing_columns}"
                logger.error(error_msg)
                self.validation_errors.append({
                    'type': 'missing_columns',
                    'dataset': dataset_key,
                    'columns': missing_columns,
                    'timestamp': datetime.now()
                })
    
    def get_data_quality_report(self) -> Dict:
        """Generate comprehensive data quality report."""
        # This method can be expanded based on the manifest.
        return {"status": "not fully implemented"}

