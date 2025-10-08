"""
CSV processing functionality for Commercial-View
Comprehensive CSV data integration for KPI calculations and analytics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CSVProcessor:
    """Process CSV files for KPI calculations and portfolio analytics"""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"CSVProcessor initialized with data directory: {self.data_dir}")

    def ingest_csv(
        self, file_content: bytes, filename: str, replace: bool = False
    ) -> Dict[str, Any]:
        """
        Ingest and process uploaded CSV file
        
        Args:
            file_content: Raw CSV file content
            filename: Name of the uploaded file
            replace: Whether to replace existing data
            
        Returns:
            Dict containing ingestion results and preview
        """
        try:
            # Parse CSV
            df = pd.read_csv(pd.io.common.BytesIO(file_content))
            
            # Determine file type based on columns
            file_type = self._detect_file_type(df)
            
            # Save to data directory
            file_path = self.data_dir / filename
            if file_path.exists() and not replace:
                raise ValueError(f"File {filename} already exists. Use replace=true to overwrite.")
            
            df.to_csv(file_path, index=False)
            
            # Generate preview
            preview = self._generate_preview(df, file_type)
            
            return {
                "success": True,
                "filename": filename,
                "file_type": file_type,
                "rows_ingested": len(df),
                "columns": list(df.columns),
                "preview": preview,
                "last_updated": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error ingesting CSV {filename}: {e}")
            raise ValueError(f"Failed to ingest CSV: {str(e)}")

    def _detect_file_type(self, df: pd.DataFrame) -> str:
        """Detect the type of CSV file based on columns"""
        columns = set(df.columns.str.lower())
        
        if "loan_id" in columns and "principal_amount" in columns:
            return "loan_data"
        elif "payment_date" in columns or "payment_amount" in columns:
            return "payment_schedule"
        elif "customer_id" in columns or "client_id" in columns:
            return "customer_data"
        else:
            return "unknown"

    def _generate_preview(self, df: pd.DataFrame, file_type: str) -> Dict[str, Any]:
        """Generate a data preview with summary statistics"""
        preview = {
            "sample_rows": df.head(5).to_dict(orient="records"),
            "summary": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": list(df.columns),
            },
        }
        
        # Add type-specific metrics
        if file_type == "loan_data":
            if "principal_amount" in df.columns:
                preview["metrics"] = {
                    "total_principal": float(df["principal_amount"].sum()),
                    "avg_loan_size": float(df["principal_amount"].mean()),
                    "loan_count": len(df),
                }
        elif file_type == "payment_schedule":
            if "payment_amount" in df.columns:
                preview["metrics"] = {
                    "total_payments": float(df["payment_amount"].sum()),
                    "payment_count": len(df),
                }
        
        return preview

    def load_csv_files(self) -> Dict[str, pd.DataFrame]:
        """Load standard CSV files for portfolio analysis"""
        files = {
            "payment_schedule": None,
            "loan_data": None,
            "historic_real_payment": None,
        }

        # Look for standard filenames
        standard_files = {
            "payment_schedule": ["payment_schedule.csv", "Payment Schedule.csv"],
            "loan_data": ["loan_data.csv", "Loan Data.csv"],
            "historic_real_payment": [
                "historic_real_payment.csv",
                "Historic Real Payment.csv",
            ],
        }

        for key, filenames in standard_files.items():
            for filename in filenames:
                file_path = self.data_dir / filename
                if file_path.exists():
                    try:
                        files[key] = pd.read_csv(file_path)
                        logger.info(f"Loaded {key} from {filename}")
                        break
                    except Exception as e:
                        logger.error(f"Error loading {filename}: {e}")

        return files

    def calculate_outstanding_portfolio(self, payment_data: pd.DataFrame) -> float:
        """Sum most recent EOM balances from payment schedule"""
        if payment_data is None or payment_data.empty:
            return 0.0

        try:
            # Group by loan and get latest balance
            if "loan_id" in payment_data.columns and "remaining_balance" in payment_data.columns:
                # Ensure data is sorted by payment_date before grouping
                if "payment_date" in payment_data.columns:
                    payment_data = payment_data.sort_values("payment_date")
                latest_balances = payment_data.groupby("loan_id")["remaining_balance"].last()
                return float(latest_balances.sum())
            elif "outstanding_balance" in payment_data.columns:
                return float(payment_data["outstanding_balance"].sum())
        except Exception as e:
            logger.error(f"Error calculating outstanding portfolio: {e}")
            
        return 0.0

    def calculate_tenor_mix(self, loan_data: pd.DataFrame) -> Dict[str, float]:
        """Group loans into tenor buckets for distribution analysis"""
        tenor_buckets = {"0-12": 0.0, "13-24": 0.0, "25-36": 0.0, "37+": 0.0}

        if loan_data is None or loan_data.empty:
            return tenor_buckets

        try:
            if "term_months" in loan_data.columns:
                for _, row in loan_data.iterrows():
                    term = row["term_months"]
                    if term <= 12:
                        tenor_buckets["0-12"] += 1
                    elif term <= 24:
                        tenor_buckets["13-24"] += 1
                    elif term <= 36:
                        tenor_buckets["25-36"] += 1
                    else:
                        tenor_buckets["37+"] += 1
                        
                # Convert to percentages
                total = sum(tenor_buckets.values())
                if total > 0:
                    tenor_buckets = {k: (v / total) * 100 for k, v in tenor_buckets.items()}
        except Exception as e:
            logger.error(f"Error calculating tenor mix: {e}")

        return tenor_buckets

    def calculate_npl_metrics(self, payment_data: pd.DataFrame) -> Dict[str, Any]:
        """Identify loans with >90 days past due"""
        npl_metrics = {"npl_count": 0, "npl_amount": 0.0, "npl_percentage": 0.0}

        if payment_data is None or payment_data.empty:
            return npl_metrics

        try:
            if "days_past_due" in payment_data.columns:
                npl_loans = payment_data[payment_data["days_past_due"] > 90]
                npl_metrics["npl_count"] = len(npl_loans)
                
                if "remaining_balance" in payment_data.columns:
                    npl_metrics["npl_amount"] = float(npl_loans["remaining_balance"].sum())
                    total_balance = float(payment_data["remaining_balance"].sum())
                    if total_balance > 0:
                        npl_metrics["npl_percentage"] = (
                            npl_metrics["npl_amount"] / total_balance
                        ) * 100
        except Exception as e:
            logger.error(f"Error calculating NPL metrics: {e}")

        return npl_metrics
