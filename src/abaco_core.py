"""
Abaco Core module extracted from PRs #26-30
Core utilities for commercial view analysis with robust error handling
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AbacoCore:
    """Core utilities for commercial lending analysis"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            "date_format": "%Y-%m-%d",
            "currency_precision": 2,
            "validation_rules": {"min_loan_amount": 1000, "max_loan_amount": 1000000},
        }
        logger.info("Abaco Core initialized successfully")

    def standardize_data_formats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize date and numeric formats across datasets"""
        if df.empty:
            logger.warning("Empty DataFrame provided for standardization")
            return df

        result_df = df.copy()

        # Date standardization with error handling
        date_columns = [
            "disbursement_date",
            "payment_date",
            "maturity_date",
            "last_active_date",
        ]
        for col in date_columns:
            if col in result_df.columns:
                try:
                    result_df[col] = pd.to_datetime(result_df[col], errors="coerce")
                    logger.debug(f"Standardized date column: {col}")
                except Exception as e:
                    logger.error(f"Error standardizing date column {col}: {e}")

        # Numeric standardization with validation
        numeric_columns = ["loan_amount", "outstanding_balance", "apr", "days_past_due"]
        for col in numeric_columns:
            if col in result_df.columns:
                try:
                    result_df[col] = pd.to_numeric(result_df[col], errors="coerce")
                    # Apply validation rules
                    if col == "loan_amount":
                        min_amount = self.config["validation_rules"]["min_loan_amount"]
                        max_amount = self.config["validation_rules"]["max_loan_amount"]
                        invalid_amounts = (
                            (result_df[col] < min_amount)
                            | (result_df[col] > max_amount)
                        ).sum()
                        if invalid_amounts > 0:
                            logger.warning(
                                f"Found {invalid_amounts} invalid loan amounts"
                            )
                except Exception as e:
                    logger.error(f"Error standardizing numeric column {col}: {e}")

        logger.info(f"Data standardization completed for {len(result_df)} records")
        return result_df

    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive data quality validation with detailed metrics"""
        quality_report = {
            "total_records": len(df),
            "missing_data": {},
            "duplicate_records": 0,
            "data_types": {},
            "quality_score": 0.0,
            "recommendations": [],
        }

        if df.empty:
            quality_report["quality_score"] = 0.0
            quality_report["recommendations"].append("Dataset is empty")
            return quality_report

        try:
            # Missing data analysis
            missing_data = df.isnull().sum()
            quality_report["missing_data"] = missing_data.to_dict()

            # Duplicate analysis
            quality_report["duplicate_records"] = int(df.duplicated().sum())

            # Data types
            quality_report["data_types"] = {
                col: str(dtype) for col, dtype in df.dtypes.items()
            }

            # Calculate quality score (0-100)
            total_cells = len(df) * len(df.columns)
            missing_cells = missing_data.sum()
            duplicate_penalty = quality_report["duplicate_records"] * len(df.columns)

            quality_score = max(
                0, 100 - ((missing_cells + duplicate_penalty) / total_cells * 100)
            )
            quality_report["quality_score"] = round(quality_score, 2)

            # Generate recommendations
            if missing_cells > 0:
                quality_report["recommendations"].append(
                    f"Address {missing_cells} missing values"
                )
            if quality_report["duplicate_records"] > 0:
                quality_report["recommendations"].append(
                    f"Remove {quality_report['duplicate_records']} duplicate records"
                )
            if quality_score < 80:
                quality_report["recommendations"].append(
                    "Data quality below 80% - review data sources"
                )

            logger.info(f"Data quality validation completed. Score: {quality_score}%")

        except Exception as e:
            logger.error(f"Error during data quality validation: {e}")
            quality_report["recommendations"].append("Data quality validation failed")

        return quality_report

    def create_data_snapshot(
        self, df: pd.DataFrame, snapshot_name: str
    ) -> Dict[str, Any]:
        """Create a data snapshot for audit trail"""
        snapshot = {
            "snapshot_name": snapshot_name,
            "timestamp": datetime.now().isoformat(),
            "record_count": len(df),
            "columns": list(df.columns),
            "summary_stats": {},
        }

        # Generate summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            snapshot["summary_stats"][col] = {
                "mean": float(df[col].mean()) if not df[col].empty else 0.0,
                "median": float(df[col].median()) if not df[col].empty else 0.0,
                "std": float(df[col].std()) if not df[col].empty else 0.0,
            }

        logger.info(f"Data snapshot '{snapshot_name}' created")
        return snapshot
